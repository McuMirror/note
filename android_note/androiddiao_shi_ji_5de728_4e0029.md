# Android調試技巧(一)




##一. 獲取Trace
調用棧信息(Trace)是分析異常經常使用的，這裡簡單劃分兩類情況：

- 當前線程Trace: 當前執行流所在線程的調用棧信息；
- 目標進程Trace：可獲取目標進程的調用棧，用於動態調試；



###1.1 當前線程Trace
1) Java層

```java
Thread.currentThread().dumpStack();   //方法1
Log.d(TAG,"Gityuan", new RuntimeException("Gityuan")); //方法2
new RuntimeException("Gityuan").printStackTrace(); //方法3
```

2） Native層


```cpp
#include <utils/CallStack.h>
android::CallStack stack(("Gityuan"));
```

### 1.2 目標進程Trace
1) Java層

```java
adb shell kill -3 [pid]     //方法1
Process.sendSignal(pid, Process.SIGNAL_QUIT)  //方法2
```

生成trace文件保存在文件data/anr/traces.txt


2） Native層

```sh
adb shell debuggerd -b [tid] //方法1
Debug.dumpNativeBacktraceToFile(pid, tracesPath) //方法2
```

前兩條命令輸出內容相同:

- 命令1輸出到控制檯
- 命令2輸出到目標文件

對於debuggerd命令，若不帶參數則輸出tombstones文件，保存到目錄/data/tombstones


3） Kernel層

```sh
adb shell cat /proc/[tid]/stack  //方法1
WatchDog.dumpKernelStackTraces() //方法2
```

其中dumpKernelStackTraces()只能用於打印當前進程的kernel線程

###1.3 小節
以下分別列舉輸出Java, Native, Kernel的調用棧方式：

```sh
類別	函數式	命令式
Java	Process.sendSignal(pid, Process.SIGNAL_QUIT)	kill -3 [pid]
Native	Debug.dumpNativeBacktraceToFile(pid, tracesPath)	debuggerd -b [pid]
Kernel	WD.dumpKernelStackTraces()	cat /proc/[tid]/stack
```

分析異常時往往需要關注的重要目錄：

```sh
/data/anr/traces.txt
/data/tombstones/tombstone_X
/data/system/dropbox/
```


##二. 時間調試
為了定位耗時過程，有時需要在關注點添加相應的systrace，而systrace可跟蹤系統cpu,io以及各個子系統運行狀態等信息，對於kernel是利用Linux的ftrace功能。當然也可以直接在方法前後加時間戳，輸出log的方式來分析。

###2.1 新增systrace

1) App

```java
import android.os.Trace;
void foo() {
    Trace.beginSection("app:foo");
    ...
    Trace.endSection(); 
}
```

2) Java Framework


```java
import android.os.Trace;
void foo() {
    Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER, "fw:foo");
    ...
    Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER); 
}
```

3） Native Framework


```cpp
#define ATRACE_TAG ATRACE_TAG_GITYUAN
#include <utils/Trace.h> // used for C++
#include <cutils/trace.h> // used for C

void foo() 
{
    ATRACE_CALL();
    ...
}
```

或者

```cpp
#define ATRACE_TAG ATRACE_TAG_GITYUAN
#include <utils/Trace.h> // used for C++
#include <cutils/trace.h> // used for C

void foo() {
    ATRACE_BEGIN();
    ...
    ATRACE_END();
}
```

### 2.2 打印時間戳

1) Java

```java
import android.util.Log;
void foo()
{
    long startTime = System.currentTimeMillis();
    ...
    long spendTime = System.currentTimeMillis() - startTime;
    Log.i(TAG,"took " + spendTime + “ ms.”);
}
```

2） C/C++

```cpp
#include <stdio.h>
#include <sys/time.h>

void foo() 
{
    struct timeval time;
    gettimeofday(&time, NULL); //精度us
    printf("took %lld ms.\n", time.tv_sec * 1000 + time.tv_usec /1000);
}
```

## 2.3 kernel log

有時候Kernel log的輸出是由級別限制，可通過如下命令查看：

```sh
adb shell cat /proc/sys/kernel/printk  
4       4       1       7
```

參數解讀：

- 控制檯日誌級別：優先級高於該值的消息將被打印至控制檯。
- 缺省的消息日誌級別：將用該值來打印沒有優先級的消息。
- 最低的控制檯日誌級別：控制檯日誌級別可能被設置的最小值。
- 缺省的控制檯日誌級別：控制檯日誌級別的缺省值


日誌級別：

<table class="table">
  <thead>
    <tr>
      <th>級別</th>
      <th>值</th>
      <th>說明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>KERN_EMERG</td>
      <td>0</td>
      <td>致命錯誤</td>
    </tr>
    <tr>
      <td>KERN_ALERT</td>
      <td>1</td>
      <td>報告消息</td>
    </tr>
    <tr>
      <td>KERN_CRIT</td>
      <td>2</td>
      <td>嚴重異常</td>
    </tr>
    <tr>
      <td>KERN_ERR</td>
      <td>3</td>
      <td>出錯</td>
    </tr>
    <tr>
      <td>KERN_WARNING</td>
      <td>4</td>
      <td>警告</td>
    </tr>
    <tr>
      <td>KERN_NOTICE</td>
      <td>5</td>
      <td>通知</td>
    </tr>
    <tr>
      <td>KERN_INFO</td>
      <td>6</td>
      <td>常規</td>
    </tr>
    <tr>
      <td>KERN_DEBUG</td>
      <td>7</td>
      <td>調試</td>
    </tr>
  </tbody>
</table>

Log相關命令

- dmesg 或 cat /proc/kmsg
- logcat -L 或 cat /proc/last_kmsg
- logcat -b events -b system


##三. addr2line
addr2line功能是將函數地址解析為函數名。分析過Native Crash，那麼對addr2line一定不會陌生。 addr2line命令參數：


```sh
Usage: addr2line [option(s)] [addr(s)]
 The options are:
  @<file>                Read options from <file>
  -a --addresses         Show addresses
  -b --target=<bfdname>  Set the binary file format
  -e --exe=<executable>  Set the input file name (default is a.out)
  -i --inlines           Unwind inlined functions
  -j --section=<name>    Read section-relative offsets instead of addresses
  -p --pretty-print      Make the output easier to read for humans
  -s --basenames         Strip directory names
  -f --functions         Show function names
  -C --demangle[=style]  Demangle function names
  -h --help              Display this information
  -v --version           Display the program's version
```

### 3.1 Native地址轉換

Step 1: 獲取symbols表

先獲取對應版本的symbols，即可找到對應的so庫。（最好是對應版本addr2line，可確保完全匹配）

Step 2: 執行addr2line命令

```sh
// 64位
cd prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin
./aarch64-linux-android-addr2line -f -C -e libxxx.so  <addr1>

//32位
cd /prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9/bin
./arm-linux-androideabi-addr2line -f -C -e libxxx.so  <addr1>
```

另外，有興趣可以研究下development/scripts/stack，地址批量轉換工具。

###3.2 kernel地址轉換
addr2line也適用於調試分析Linux Kernel的問題。例如，查詢如下命令所對應的代碼行號

```sh
[<0000000000000000>] binder_thread_read+0x2a0/0x324
```


Step 1: 獲取符號地址

通過命令arm-eabi-nm從vmlinux找到目標方法的符號地址，其中nm和vmlinux所在目錄：

- arm-eabi-nm位於目錄prebuilts/gcc/linux-x86/arm/arm-eabi-4.8/bin/
- vmlinux位於目錄out/target/product/xxx/obj/KERNEL_OBJ/

執行如下命令：(需要帶上絕對目錄)

```sh
arm-eabi-nm  vmlinux |grep binder_thread_read
```

則輸出結果： `c02b2f28 T binder_thread_read`，可知binder_thread_read的符號地址為c02b2f28， 其偏移量為0x2a0，則計算後的目標符號地址= c02b2f28 + 2a0，然後再採用addr2line轉換得到方法所對應的行數

Step 2: 執行addr2line命令

```sh
./aarch64-linux-android-addr2line -f -C -e vmlinux [目標地址]
```

注意:對於kernel調用棧翻譯過程都是通過vmlinux來獲取的


---


##三、JAVA層堆棧列印
###1. 在指定的函數內列印相關java調用

```java
Log.d(TAG,Log.getStackTraceString(new Throwable()));
```

###2. 普通JAVA進程堆棧

```java
ActivityManagerService.dumpStackTraces
```

保存在系統設置dalvik.vm.stack-trace-file指定的文件data/anr/traces.txt中。可以包含多個進程堆棧資訊。

###3. 內核進程堆棧

```java
dumpKernelStackTraces，該函數為私有函數，不可調用。
```

代碼在frameworks/base/services/java/com/android/server/Watchdog.java

保存在系統設置dalvik.vm.stack-trace-file指定的文件data/anr/traces.txt中。

###4. 出異常時列印當前堆棧

```java
Exception::printStackTrace()


try {
 ...
} catch (RemoteException e) {
  e.printStackTrace();
  ...
}
```

###5. 輸出指定進程的堆棧

```java
Process.sendSignal(pid, Process.SIGNAL_QUIT)
```

保存在data/anr/traces.txt。

這個只對java進程有效，由dalvikvm的SignalCatcher.c處理。

## 四、Native層堆棧列印

###1. CallStack
使用方式:

```cpp
#include <utils/CallStack.h>
...
CallStack stack;
stack.update();
stack.dump("");  // the parameter is prefix of dump
```

在使用之前需要修改system/core/include/arch/linux-arm/AndroidConfig.h



在使用之前需要修改system/core/include/arch/linux-arm/AndroidConfig.h

```cpp
#define HAVE_DLADDR 1
#define HAVE_CXXABI 1
```

並在文件frameworks/base/libs/utils/Android.mk中大約105行（LOCAL_SHARED_LIBRARIES）後添加


```cpp
ifeq ($(TARGET_OS),linux)
  LOCAL_SHARED_LIBRARIES += libdl
endif
```

重新編譯，push生成的libutils.so到/system/lib/目錄下，重啟設備。


##五、JAVA異常分析
這個android會輸出資訊到logcat。容易分析。

##六、Natvie異常分析
native進程異常會導致

debuggerd會輸出資訊到logcat並保存到/data/tombstones。

可以修改system/core/debuggerd/debuggerd.c中dump_stack_and_code的代碼滿足更深的調試資訊需求。

Natvie異常分析(dalvik方式）
用此方法調試由於GC導致的native異常。

```cpp
修改vm/interp/Stack.c約456行的dvmCallMethodV函數，添加以下幾行。

LOGD(" YINGMINGBO class:%s\n", clazz->descriptor);
LOGD(" YINGMINGBO name:%s\n", method->name);
LOGD(" YINGMINGBO desc:%s\n", desc);
```


##七、日誌Log系統
在java中使用
```java
import android.util.Log;
...
Log.d(TAG,"log info");
```

在Native代碼中使用

```cpp
#define LOG_TAG "YOUR_LOGTAG"
...
#include <utils/Log.h>
#define LOG_NDEBUG 0
...
LOGD("log info");
```

或者

```cpp
Log.d(LOG_TAG,“log info”);
```

使用adb logcat時可以只顯示特定類別的LOG，還可以通過參數 -v threadtime 顯示線程號及時間資訊。

普通標準輸出轉為Logcat

```cpp
#system/bin/logwrapper 進程名
```

##八、其他調試手段（命令行）
###1. 列印指定JAVA進程的堆棧到文件中

```sh
#kill -3 pid
```

這裡的3就是3.5節的Process.SIGNAL_QUIT。

輸出在`data/anr/traces.txt`文件中。

這個`只對java進程有效，由dalvikvm處理`。

###2. 列印指定進程的堆棧到Logcat

```sh
#kill -11 pid
或者
#kill -7 pid
```

這個有時有效。其原理是利用了（六）節的機制。

可以用adb logcat看堆棧調用輸出。

###3. 列印指定進程的系統調用

```sh
#strace -f -p pid -o output
```

主要輸出文件、SOCKET、鎖等系統操作的資訊。

-f表示跟蹤所有子進程.

-o輸出log到指定文件，可不用。
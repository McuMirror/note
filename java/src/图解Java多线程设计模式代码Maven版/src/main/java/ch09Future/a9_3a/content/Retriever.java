package ch09Future.a9_3a.content;

public class Retriever {
    public static Content retrieve(final String urlstr) {
        final AsyncContentImpl future = new AsyncContentImpl();

        new Thread() {
            public void run() {
                future.setContent(new SyncContentImpl(urlstr));
            }
        }.start();

        return future;
    }
}

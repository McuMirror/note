/*
 * Copyright (C) 2016 Daniel Himmelein
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "mindroid/lang/Short.h"
#include "mindroid/lang/String.h"
#include <cstdlib>

namespace mindroid
{

sp<Short> Short::valueOf(const char* s)
{
    return new Short(strtol(s, nullptr, 10));
}

sp<Short> Short::valueOf(const sp<String>& s)
{
    return valueOf(s->c_str());
}

sp<Short> Short::valueOf(const char* s, int32_t radix)
{
    return new Short(strtol(s, nullptr, radix));
}

sp<Short> Short::valueOf(const sp<String>& s, int32_t radix)
{
    return valueOf(s->c_str(), radix);
}

} /* namespace mindroid */

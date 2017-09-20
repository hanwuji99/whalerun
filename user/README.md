# whale.run services - user

## 系统环境变量设置

    PROJECT_DOMAIN
    FLASK_LOGFILE (default: whalerun_user.log)
    FLASK_MYSQL_HOST (default: localhost)
    FLASK_MYSQL_PORT (default: 3306)
    FLASK_MYSQL_USER (default: root)
    FLASK_MYSQL_PASSWORD
    FLASK_MYSQL_DB (default: whalerun_user)
    FLASK_REDIS_HOST (default: localhost)
    FLASK_REDIS_PORT (default: 6379)
    FLASK_REDIS_DB (default: 0)
    CELERY_BROKER_DB (default: 1)
    CELERY_BACKEND_DB (default: 2)
    SMTP_SERVER (default: smtpdm.aliyun.com)
    SMTP_FROM_ADDR
    SMTP_PASSWORD
    DES_KEY (8 bytes) (default: ********)

## API Overview

**All data is sent and received as JSON.**

**success response**

    {
        code: 0
        message: 'Success'
        data: {
            [响应数据]
        }
    }

**error response**

    {
        code: [错误码]
        message: [错误信息]
        data: {}
    }

**错误码对应错误信息**

    1000: 'Internal Server Error'
    1100: 'Bad Request'
    1101: 'Unauthorized'
    1103: 'Forbidden'
    1104: 'Not Found'
    1201: 'GET方法url参数不完整'
    1202: 'GET方法url参数值错误'
    1401: 'POST/PUT方法json数据不完整'
    1402: 'POST/PUT方法json数据值或类型错误'
    1410: '邮箱格式错误'
    1411: '账号不存在'
    1412: '账号已存在'
    1413: '密码错误'
    1414: '密码长度错误'
    1415: '验证码错误'
    1416: '验证码已过期'
    1417: '用户已验证邮箱'
    1418: '用户未验证邮箱'
    1601: 'DELETE方法url参数不完整'
    1602: 'DELETE方法url参数值错误'

**某些情况下通用的错误码**

    所有请求：1000
    POST/PUT方法：1100
    使用分页参数page/per_page：1202

**通用的可选URL参数**

    fields: 指定返回的对象数据中只包含哪些字段，多个字段以英文逗号分隔

## API References

**获取当前用户详情**

    GET  /api/current_user/

    必填URL参数：
        token: 身份令牌

    响应数据：
        user [object]:

    错误码：
        1104, 1201

**列出用户**

    GET  /api/users/

    可选URL参数：
        ids: 用户id，多个值以英文逗号分隔
        uuids: 用户uuid，多个值以英文逗号分隔
        order_by:
        page:
        per_page:
        email: 邮箱
        email_verified: 是否已验证邮箱：0 - 否，1 - 是
        blocked: 是否禁止登录：0 - 否，1 - 是
        featured: 是否推荐：0 - 否，1 - 是

    响应数据：
        users [object_array]:
        total [int]:

    错误码：
        1202

**创建用户**

    POST  /api/users/

    必填数据字段：
        email [string]: 邮箱
        password [string]: 密码
        name [string]: 昵称

    响应数据：
        user [object]:
        token [string]:

    错误码：
        1401, 1402, 1410, 1412, 1414

**用户登录**

    PUT  /api/users/login/

    必填数据字段：
        email [string]: 邮箱
        password [string]: 密码

    响应数据：
        user [object]:
        token [string]:

    错误码：
        1103, 1401, 1402, 1411, 1413

**发送验证邮件（链接）**

    POST  /api/users/verification_email/

    可选数据字段：
        # user_id与email二选一
        user_id [int]: 用户id
        email [string]: 邮箱

    错误码：
        1401, 1411, 1417

**用户邮箱通过验证**

    PUT  /api/users/email_verified/

    必填数据字段：
        user_uuid [string]: 用户uuid
        token [string]: 身份令牌

    响应数据：
        user [object]:

    错误码：
        1401, 1411

**修改用户密码**

    PUT  /api/users/password/

    必填数据字段：
        password_new [string]: 新密码

    可选数据字段：
        # user_id与email二选一
        user_id [int]: 用户id
        email [string]: 邮箱

        # code与password_old二选一
        code [string]: 验证码
        password_old [string]: 旧密码

    响应数据：
        user [object]:

    错误码：
        1401, 1402, 1411, 1413, 1414, 1415, 1416

**修改用户昵称**

    PUT  /api/users/name/

    必填数据字段：
        name [string]: 昵称

    可选数据字段：
        # user_id与email二选一
        user_id [int]: 用户id
        email [string]: 邮箱

    响应数据：
        user [object]:

    错误码：
        1401, 1402, 1411

**修改用户头像**

    PUT  /api/users/avatar/

    可选数据字段：
        # user_id与email二选一
        user_id [int]: 用户id
        email [string]: 邮箱

        avatar [string]: 头像图片url

    响应数据：
        user [object]:

    错误码：
        1401, 1402, 1411

**创建验证码**

    POST  /api/captcha/

    必填数据字段：
        group [int]: 分组：1 - 找回密码验证码

    可选数据字段：
        # user_id与email二选一
        user_id [int]: 用户id
        email [string]: 邮箱

    响应数据：
        captcha [object]:

    错误码：
        1401, 1402, 1411

**核对验证码**

    PUT  /api/captcha/check/

    必填数据字段：
        group [int]: 分组：1 - 找回密码验证码
        code [string]: 验证码

    可选数据字段：
        # user_id与email二选一
        user_id [int]: 用户id
        email [string]: 邮箱

    错误码：
        1401, 1402, 1411, 1415, 1416

## Model Dependencies

_- : on_delete='CASCADE'_

_* : on_delete='CASCADE', null=True_

**User**

    - : Captcha

**Captcha**

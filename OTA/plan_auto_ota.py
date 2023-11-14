
import logging
import sys,os
import oss2
import hashlib
import datetime,time
from oss2.models import PartInfo
from oss2 import determine_part_size
import requests,json
from time import strftime,localtime


# 阿里云 OSS 访问参数
access_key_id = 'LTAI5tNBCfeZ8WkmeR7SiyRc'
access_key_secret = 'wPNDIh0GoY2wxVFKw8jxbbQNPPqJkO'
endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'
bucket_a_name = 'rokid-glass-ota'
bucket_b_name = 'rokid-ota'

# OSS 文件夹路径
dailybuild_folder_path = 'dailybuild/glass11/'
ota_folder_path = 'YodaOS-Master/OS/StationPro/'

# 创建 OSS 客户端，创建Bucket对象
auth = oss2.Auth(access_key_id, access_key_secret)
bucket_a = oss2.Bucket(auth, endpoint, bucket_a_name)
bucket_b = oss2.Bucket(auth, endpoint, bucket_b_name)

#url address
url_cdn = 'https://ota-g.rokidcdn.com/'
login_url = 'https://developer.rokid.com/rokid-ota/login'
add_url = 'https://developer.rokid.com/rokid-ota/ota/rockid/doSave?status=2'

# 登录镜像发布系统所需的用户名和密码
username = 'guojun.fang'
password = 'Fang@1234'

# 钉钉群机器人的 Webhook 钉钉群： YodaOS-Master（代号纳布）
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=20b3c71efa53b68f93c8faaa84a0fa761e0cf081fb5ecd01d2d168a3c2795f29"
headers = {
    'Content-Type': 'application/json'
}
# 定义钉钉要发送的消息内容
message = {
    'msgtype': 'text',
    'text': {
        'content': 'send your message！'
    }
}
push_message_daily = "【YodaOS-Master Dailybuild】日构建版本 （OTA自动推送）"
push_message_release = "【YodaOS-Master Release】提测版本 （OTA自动推送）"

# 定义LogFolder目录路径
log_folder = './LogFolder'

# 如果LogFolder目录不存在，则创建它
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
#定义其他参数
url_md5_record = './url_md5_record.txt'

# 如果url_md5_record.txt文件不存在，则创建它
if not os.path.exists(url_md5_record):
    with open(url_md5_record, 'w') as file:
        # 可以选择在文件中写入一些初始内容
        file.write('Record URL and MD5!\n')

ota_md5_url = {}
version_list=[]

# 创建一个会话对象
session = requests.Session()

devices_group = {
    "StationPro_XR中心_黑名单" : "1687383488732332032",
    "StationPro_XR中心_EVT" : "1663394784204554240",
    "StationPro_EVT_null" : "1699253880535121920",
    "StationPro_DVT" : "1687318571543166976",
    "StationPro_DVT_黑名单" : "1687385755191607296",
    "StationPro_DVT_个人" : "1687319811102605312",
    "StationProEVT_QA_release" : "1702152007571210240",
    "StationProDVT_QA_release" : "1702153809817501696",
}
dev_grps_ids1_xr = "1663394784204554240,1687318571543166976"
dev_grps_ids2_null = "1699253880535121920"
dev_grps_ids3_qa = "1702152007571210240,1702153809817501696"
dev_grps_ids4_rel = "1663394784204554240,1687318571543166976,1702153809817501696"

#dev_grps_ids1_xr = "1699253880535121920"
#dev_grps_ids2_null = "1699253880535121920"
#dev_grps_ids3_qa = "1699253880535121920"

# 日志设置
def setup_logger():
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_folder, f'log_{current_date}.log')

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

logger = setup_logger()


def Has_new_OS():
    newVersion=""
    tmp_time = 0
    has_new_object = False
    # 获取当天 02:00 、06:00的时间戳
    today0 = datetime.datetime.now().strftime('%Y%m%d')
    today1 = datetime.datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
    today6 = datetime.datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    today1_timestamp = int(today1.timestamp())
    #today6_timestamp = int(today6.timestamp())
    today2_timestamp = int(time.time())

    # 获取 OS 文件夹下的所有文件和文件夹列表
    object_list = []
    for obj in oss2.ObjectIterator(bucket_a, prefix=dailybuild_folder_path):
        if obj.key[-1] == '/' and today0 in str(obj.key):
            # 获取文件/文件夹的最后修改时间
            obj_meta = bucket_a.get_object_meta(obj.key)
            last_modified = obj_meta.last_modified
            # 判断是否有0点到当前时间的镜像文件
            if last_modified > today1_timestamp and last_modified < today2_timestamp:
                if last_modified > tmp_time: 
                    tmp_time = last_modified
                    has_new_object = True
                    newVersion = obj.key
                    continue
    return (newVersion,has_new_object)

#确认需要复制的文件
def Find_keys(bucket,dir):
    src_keys = []
    objects = bucket.list_objects(prefix=dir).object_list
    sorted_objects = sorted(objects, key=lambda obj: obj.size)
    for obj in sorted_objects:
        if obj.key[-1] != '/':
            src_keys.append(obj.key)
    if len(src_keys) < 1:
        logger.error(f"{source_dir}为空文件夹!")
        logger.info("～～～脚本运行结束！～～～")
        sys.exit(1)
    # elif len(src_keys) != 5:
    #     logger.error(f"【E】{source_dir} 文件夹内文件数量不符合预期（预期=5个文件)!")
    #     sys.exit(1)
    else:
        return src_keys
        
def Get_diff_version(src_keys_list):
    diff_version_name = ""
    min_version_name = ""
    for src_key in src_keys_list:
        file_name = src_key.split("/")[-1]
        if file_name.count('-') > 4 and '-ota-' in file_name:
                base_n_name = os.path.splitext(file_name)[0].split('-ota-')[-1]
                n_list = base_n_name.split('-')
                diff_version_name = n_list[0] + '-' + n_list[1] + '-' + n_list[2]
                min_version_name = n_list[3] + '-' + n_list[4] + '-' + n_list[5]
    logger.info(f"diff_version: {diff_version_name}, min_version: {min_version_name}")
    return (diff_version_name,min_version_name)        

def Copy_file(bucket_a, bucket_b,source_key,target_key,max_retries=3):
    # 获取文件大小，用于计算进度
    file_size = bucket_a.head_object(source_key).content_length
    # 设置分块大小，根据实际情况设置
    part_size = determine_part_size(file_size, preferred_size=1024 * 1024 * 20)
    # 初始化分块上传任务
    upload_id = bucket_b.init_multipart_upload(target_key).upload_id
    parts = []
    retry_count = 0

    while retry_count < max_retries:
        try:
            part_number = 1
            offset = 0
            # 分块上传文件
            logger.info(f"{target_key} 开始上传....")
            while offset < file_size:
                num_to_upload = min(part_size, file_size - offset)
                end = offset + num_to_upload - 1
                # 上传分块      
                result = bucket_b.upload_part_copy(bucket_a.bucket_name, source_key, (offset, end), target_key, upload_id, part_number)
                # 保存part信息
                parts.append(PartInfo(part_number, result.etag))
                offset += num_to_upload
                part_number += 1
                rate = int(100 * (float(offset) / float(file_size)))
                logger.info(f'上传进度 {rate}% ....')
            # 完成分块上传任务
            bucket_b.complete_multipart_upload(target_key, upload_id, parts)
            break
        except Exception as e:
            logger.error(f' 文件传输异常！{str(e)}\n')
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"等待60s后重试...")
                time.sleep(60)
            else:
                logger.error(f"重试次数超过最大限制，上传失败！～～～")
                raise

# 遍历目标文件夹下的文件，检查是否已经存在并且大小一样，否则进行复制操作(仅复制含有ota的文件名)
def Check_Trans_Record(src_key):
    version = ""
    url = ""
    md5 = ""
    file_name = src_key.split('/')[-1]
    target_key = target_dir +'/'+ file_name
    file_size_a = bucket_a.head_object(src_key).content_length
    if bucket_b.object_exists(target_key):
        # 文件已存在
        file_size_b = bucket_b.head_object(target_key).content_length
        if file_size_a == file_size_b:
            # 文件大小相同，不需要复制
            logger.info(f'File: {target_key} 已复制成功!\n')
            if '-ota-' in file_name:
                logger.info("MD5校验中...（需耗时数分钟）")
                content_a = bucket_a.get_object(src_key).read()
                md5 = hashlib.md5(content_a).hexdigest()
                url = url_cdn + target_key
                logger.info(f'【{file_name}】---MD5: {md5} \n')
                logger.info(f'【{file_name}】---URL: {url} \n')
                base_file_name = os.path.splitext(file_name)[0].split('-ota-')[-1]
                version_name_list = base_file_name.split('-')
                version = version_name_list[0] + '-' + version_name_list[1] + '-' +version_name_list[2]
                #写入txt文件
                Write_txt_info(version,url,md5)
        else:
            # 文件大小不同，重新复制（未进行md5判断，因为md5判断比较耗时）
            logger.warning(f'{target_key} 文件大小不同，即将重新复制......') 
            # 复制文件并打印进度条
            Copy_file(bucket_a, bucket_b, src_key, target_key)
            Check_Trans_Record(src_key)
    else:
        logger.info(f'{target_key} 不存在，即将进行复制......')  
        # 复制文件并打印进度条
        Copy_file(bucket_a, bucket_b, src_key, target_key)
        Check_Trans_Record(src_key)
    return(url,md5)
    
def pay_load(version,url,md5,min_ver,groupsId,versionType="Beta",exclude_objects="1",groupsOut="",all_or_diff="1",iS_force="1",push_m=push_message_daily):
    version_1 = version.split("-")[0]
    version_2 = version.split("-")[1]
    version_3 = version.split("-")[2]

    add_payload = {
            "version_one": version_1,
            "version_two": version_2,
            "version_three": version_3,
            "hard_support_version": "Staion Pro",
            "min_soft_version": min_ver,
            "sub_version": versionType,
            #1-全量 2-增量
            "package_choice": all_or_diff,
            #1-强制升级 2-可选升级
            "is_force_update": iS_force,
            "image_url": url,
            "image_md5": md5,
            "update_description": push_m,
            "publish_objects": "2",
            #"groupsId": "1687318571543166976,1663394784204554240",
            "groupsId": groupsId,
            #若增加黑名单，则需设置 exclude_objects="2"
            "exclude_objects": exclude_objects,
            "groupsIdOut": groupsOut
            }
    #print(add_payload)
    return add_payload

def LoginOta():
    trytime = 0
    # 发送登录请求
    login_payload = {'username': username, 'password': password}
    login_response = session.post(login_url, data=login_payload)
    # 检查登录是否成功
    if login_response.status_code == 200:
        logger.info(f'登录成功!')
    elif trytime < 3:
        login_response = session.post(login_url, data=login_payload)
    else:
        logger.warning(f'镜像发布账号登录失败！')
        logger.info("～～～脚本运行结束！～～～")
        sys.exit(1)

def Check_ota(version):
    is_push = False
    LoginOta()
    get_url = "https://developer.rokid.com/rokid-ota/ota/version/?version="+version
    get_response = session.get(get_url)
    if "gradeX" in get_response.text:
        logger.info(f'{version}已在OTA镜像系统发布！\n')
        is_push = True       
    else:
        logger.info(f'{version}还未在镜像系统发布,将传输文件和发布...\n')
    return is_push

def Add_OS(version,payload,url=add_url):
    logger.info(f'即将进行OTA推送......')
    # 发送POST请求
    add_response = session.post(url, data=payload)
    # 检查 POST 请求是否成功
    if '"status":"1"' in add_response.text:
        time.sleep(2)
        if Check_ota(version):
            logger.info(f"版本{version} OTA 已发布！～～～")
            # 发送钉钉消息
            if len(version.split('-')[-1]) == 7:
                all_or_diff_txt = "差分"
                if "8001" in version.split('-')[-1]:
                    push_obj = "空组"
                else:
                    push_obj = "Release测试组"
            else:
                all_or_diff_txt = "全量"
                if "8001" in version.split('-')[-1]:
                    push_obj = "Dailybuild版本.体验组"
                else:
                    push_obj = "Release分支版本.内测组"
            message["text"]["content"] = (f'【 YodaOS Version 】：{version} 已推送OTA {all_or_diff_txt}强制升级！\n'
                                f'【推送范围】：{push_obj}\n'
                                '【升级提醒】：\n'
                                '   *需确保设备正常联网 \n'
                                '   *设备电量 >30% & 设备存储空间足够 \n'
                                '   *设备未被root&remount过 \n'
                                '   *若升级到50%失败，执行命令后再次升级：adb root && adb enable-verity && adb reboot'
                                )
            #print(message)
            dingding_response = requests.post(webhook_url, data=json.dumps(message), headers=headers)
            logger.info(f'【钉钉】Message {message}\n')
            if dingding_response.status_code == 200:
                logger.info('【钉钉】Message sent successfully.\n')
            else:
                logger.warning('【钉钉】Failed to send message.\n')
        else:
            logger.warning(f" OTA 已发布，但未查询到发布记录，请确认检查！\n")   
    else:
        logger.warning(f" OTA 自动发布失败！")
        logger.warning(add_response.text)


#以追加的形式将url、md5记录到txt中
def Write_txt_info(version,url,md5,file_path=url_md5_record):
    content_to_write = version + "," + url + "," + md5  + "\n"
    with open(file_path, "a") as file:
        file.write(content_to_write)
        
def Get_txt_info(version,min_version,file_path=url_md5_record):
    if not os.path.exists(file_path):
        logger.info(f"{file_path} 不存在!")
    else:
        # 读取文件的每一行
        with open(file_path, "r") as file:
            lines = file.readlines()
        # 处理每一行并获取相应的值
        for line in lines:
            parts = line.strip().split(",")
            if version == parts[0] and len(parts) == 3:
                url = parts[1]
                md5 = parts[2]
                logger.info(f"{version}的url/md5已存在txt文件中:\n     url: {url},\n     md5: {md5}")
                #将获取的信息塞到pay_load中 ,8001是日构建，8002是release版本              
                #差分包
                if len(version.split('-')[-1]) == 7:
                    if "8001" in version.split('-')[-1]:
                        add_pay_load = pay_load(version,url,md5,min_version,groupsId=dev_grps_ids2_null,all_or_diff="2")
                    else:
                        add_pay_load = pay_load(version,url,md5,min_version,groupsId=dev_grps_ids3_qa,all_or_diff="2",push_m=push_message_release)
                else:
                    min_version='0'
                    if "8001" in version.split('-')[-1]:
                        add_pay_load = pay_load(version,url,md5,min_version,groupsId=dev_grps_ids1_xr,exclude_objects="2",groupsOut=dev_grps_ids3_qa)
                    else:
                        add_pay_load = pay_load(version,url,md5,min_version,groupsId=dev_grps_ids4_rel,push_m=push_message_release)
                return(add_pay_load)
        return False      

def Push_ota(v,min_version,src_keys):
    #从txt中获取pay_load"
    add_pay_load = Get_txt_info(v,min_version)
    if add_pay_load:
        #logger.info("不发OTA！")
        Add_OS(v,payload=add_pay_load)
    else:
        #传输文件
        for src_key in (src_keys):
            logger.info(f'正在check和传输{src_key}......')
            Check_Trans_Record(src_key)
        Push_ota(v,min_version,src_keys)                

if __name__ == "__main__":
    # 主逻辑代码: 根据版本号查看是否已经发布ota-- check 是否存在url、md5 --- check oss是否存在文件 -- 获取payload -
    #未带参数，则获取当天的版本
    if len(sys.argv) == 1:
        obj_key,has_new_object = Has_new_OS()
        if has_new_object:
            version = obj_key.split("/")[-2]
        else:
            logger.info("截至到此时，今日无系统版本！")
            sys.exit(0)
    #带参数，则从命令行获取版本、是否提测版本
    elif len(sys.argv) == 2:
            version = sys.argv[1]
    else:
        logger.info("输入命令有误！请输入：python3 xxx.py [OSversion]")
        sys.exit(1)
    logger.info(f'\n\n\n==================================== {version} ====================================\n')
    
    version_list.append(version)
    # 获取源和目标文件夹名
    source_dir = dailybuild_folder_path + version
    target_dir = ota_folder_path + version
    try:
        src_keys = Find_keys(bucket_a,source_dir)
        diff_version,min_version = Get_diff_version(src_keys)
        #0918:不发布差分包的ota
        # if len(diff_version):
        #     version_list.append(diff_version)
            
        for v in version_list:
            logger.info(f'正在check {v} 是否已OTA发布......')
            is_push = Check_ota(v)
            if is_push:
                continue
            else:
                Push_ota(v,min_version,src_keys)
                
    except Exception as e:
        logger.error(e)
        logger.info("～～～脚本运行异常结束！～～～")
        sys.exit(1)

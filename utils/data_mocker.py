#!/usr/bin/python
# -*- coding: UTF-8 -*-
# --Author: Bernard--
import random
import time
import datetime
from faker import Faker
from faker.providers import BaseProvider
try:
    from sql_connect import MySql
except ImportError:
    MySql = None


fake = Faker('zh-CN')


class MyProvider(BaseProvider):
    _COMPANY_SUFFIXES = ['公司', '店', '厂', '院', '有限公司', '有限责任公司']
    _CAR_NO_PROVINCES = ['京', '津', '冀', '晋', '内', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '渝', '川', '黔', '滇', '藏', '陕', '甘', '青', '宁', '新', '港', '澳', '台', '军', '使', 'WJ']
    _CAR_NO_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _CAR_NO_DIGITS = '012346789'

    _SOCIAL_CREDIT_CHARS_MAP1 = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'J': 18, 'K': 19, 'L': 20, 'M': 21,
        'N': 22, 'P': 23, 'Q': 24,
        'R': 25, 'T': 26, 'U': 27, 'W': 28, 'X': 29, 'Y': 30
    }
    _SOCIAL_CREDIT_WEIGHTING_FACTOR = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]

    _ORGANIZATION_CODE_CHARS_MAP = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19, 'K': 20, 'L': 21,
        'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26,
        'R': 27, 'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35
    }
    _ORGANIZATION_CODE_WEIGHTING_FACTOR = [3, 7, 9, 10, 5, 8, 4, 2]

    _CAR_CODE_CHARS = '012346789ABCDEFGHJKLMNPRSTUVWXY'
    _CAR_CODE_MAP1 = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
    }
    _CAR_CODE_WEIGHT_MAP = {
        1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 10, 9: 0, 10: 9,
        11: 8, 12: 7, 13: 6, 14: 5, 15: 4, 16: 3, 17: 2
    }

    _PASSPORT_PREFIXES = ['14', '15', 'G', 'P', 'S', 'D']
    _PASSPORT_DIGITS = '012346789'

    _ORGANIZATION_WEIGHTS = [3, 7, 9, 10, 5, 8, 4, 2]

    _ENTERPRISE_CODE_DIGITS = '012346789'
    _ENTERPRISE_CODE_PREFIXES = '123467'

    _INDIVIDUAL_BUSINESS_SUFFIXES = [
        '商行', '庄', '部', '厂', '店', '坊', '室', '场', '美发沙龙店', '烟花爆竹店', '美容美体店', '酸辣粉店',
        '酸菜鱼馆', '麻辣烫店', '缝纫机店', '私房菜馆', '农家菜馆', '五金电机', '商业银行', '股份银行',
        '手工编织', '羊毛衫厂', '美发天地', '木业经营'
    ]
    _OFFICER_CARD_PREFIXES = [
        '军', '兵', '士', '文', '职', '军离', '军退', '武', '武离', '武退', '南', '北', '沈', '兰',
        '成', '济', '广', '参', '证', '后', '装', '海', '空'
    ]
    _OFFICER_CARD_DIGITS = '012346789'
    _SPECIAL_CHARACTERS = '~!@#$%^&*()_+-<>?|.,-/'
    _MINORITY_NAMES = [
        '阿衣努尔·阿依古丽', '巴合提古丽·叶尔木拉提', '叶尔阿斯力·如娜仁', '吉日嘎拉·敖登格日乐', '巴雅尔', '乌日塔那顺', '迪丽热巴·迪力木拉提'
    ]

######################## 17种内置隐私类型 ##############################################

    # 1、中文地址--可变长地址--限制长度500以内
    @staticmethod
    def get_address(length=None):
        if length:
            base_str = ''.join(fake.address() for _ in range(50))
            return base_str[:length]
        return fake.address()

    # 2、银行卡号
    @staticmethod
    def get_bank_card():
        return fake.credit_card_number()

    # 3、电子邮件
    @staticmethod
    def get_email():
        return fake.email()

    # 4、企业名称
    @classmethod
    def get_company_name(cls):
        first = fake.address()[:7]
        second = fake.company()[:4]
        third = random.choice(cls._COMPANY_SUFFIXES)
        return f"{first}{second}{third}"

    @classmethod
    def get_company(cls):
        return cls.get_company_name()

    # 5、中文姓名
    @staticmethod
    def get_name():
        return fake.name()

    @staticmethod
    def get_optional_name():
        return random.choice(['', fake.name()])

    # 6、身份证
    @staticmethod
    def get_id_no():
        return fake.ssn()

    @staticmethod
    def get_id_card():
        return MyProvider.get_id_no()

    # 7、电话
    @staticmethod
    def get_phone():
        return fake.phone_number()

    @staticmethod
    def get_phone_number():
        return MyProvider.get_phone()

    @staticmethod
    def get_fix_phone():
        return MyProvider.get_phone()

    # 8、邮政编码
    @staticmethod
    def get_post_code():
        return fake.postcode()

    # 9、车牌号码fake.license_plate()
    @classmethod
    def get_car_no(cls):
        province = random.choice(cls._CAR_NO_PROVINCES)
        alpha = random.choice(cls._CAR_NO_ALPHABET)
        digits = ''.join(random.sample(cls._CAR_NO_DIGITS, 5))
        return f"{province}{alpha}{digits}"

    # 10、社会信用账号 @最后一位
    @classmethod
    def get_social_credit_code(cls):
        code = cls.get_number(16)
        code = cls._create_c9(code)
        ontology_code = code[0:17]
        tmp_check_code = cls._gen_check_code(
            cls._SOCIAL_CREDIT_WEIGHTING_FACTOR, ontology_code, 31, cls._SOCIAL_CREDIT_CHARS_MAP1)
        return ontology_code + tmp_check_code

    @classmethod
    def _create_c9(cls, code):
        organization_code = code[8:17]
        ontology_code = organization_code[0:8]
        tmp_check_code = cls._gen_check_code(
            cls._ORGANIZATION_CODE_WEIGHTING_FACTOR, ontology_code, 11, cls._ORGANIZATION_CODE_CHARS_MAP
        )
        return code[:16] + tmp_check_code

    @staticmethod
    def _gen_check_code(weighting_factor, ontology_code, modulus, check_code_dict):
        total = 0
        for i, char in enumerate(ontology_code):
            if char.isdigit():
                total += int(char) * weighting_factor[i]
            else:
                total += check_code_dict[char] * weighting_factor[i]
        c9_val = modulus - total % modulus
        c9_val = 0 if c9_val == modulus else c9_val
        return list(check_code_dict.keys())[list(check_code_dict.values()).index(c9_val)]

    # 11、汽车车架号
    @classmethod
    def get_car_code(cls):
        car_code_list = random.sample(cls._CAR_CODE_CHARS, 17)
        total_sum = 0
        for i, char in enumerate(car_code_list):
            if i == 8:
                continue
            num1 = cls._CAR_CODE_MAP1[char]
            num2 = cls._CAR_CODE_WEIGHT_MAP[i + 1]
            total_sum += num1 * num2

        remainder = total_sum % 11
        tar_char = 'X' if remainder == 10 else str(remainder)

        car_code_list[8] = tar_char
        return "".join(car_code_list)

    # 12、护照
    @classmethod
    def get_passport(cls):
        first = random.choice(cls._PASSPORT_PREFIXES)
        passport = first + ''.join(random.sample(cls._PASSPORT_DIGITS, (9-len(first))))
        return passport

    # 13、税务登记证号
    @staticmethod
    def get_tax_code():
        list1 = ['0', '1', '2', '3', '4', '6', '7', '8', '9']
        last = ''.join(random.sample(list1, 2))
        return str(fake.ssn()) + last

    # 14、组织机构代码
    @classmethod
    def get_organization(cls):
        cc = [str(random.randint(1, 9)) for _ in range(8)]
        dd = sum(int(c) * w for c, w in zip(cc, cls._ORGANIZATION_WEIGHTS))
        c9 = 11 - dd % 11
        if c9 == 10:
            c9_char = 'X'
        elif c9 == 11:
            c9_char = ''
        else:
            c9_char = str(c9)
        return "".join(cc) + '-' + c9_char

    # 15、营业执照代码
    @classmethod
    def get_enterprise_code(cls):
        first = random.choice(cls._ENTERPRISE_CODE_PREFIXES)
        second = ''.join(random.sample(cls._ENTERPRISE_CODE_DIGITS, 5))
        third = '6'
        fourth = ''.join(random.sample(cls._ENTERPRISE_CODE_DIGITS, 7))
        # 查不到校验规则，暂时搁置
        end = random.choice(cls._ENTERPRISE_CODE_DIGITS)
        return f"{first}{second}{third}{fourth}{end}"

    # 16、单体商户名称
    @classmethod
    def get_individual_business(cls):
        company = fake.company().replace('有限公司', '')
        shop = company + random.choice(cls._INDIVIDUAL_BUSINESS_SUFFIXES)
        return shop

    # 17、军官警官证编号
    @classmethod
    def get_officer_card(cls):
        prefix = random.choice(cls._OFFICER_CARD_PREFIXES)
        number = ''.join(random.sample(cls._OFFICER_CARD_DIGITS, 7))
        return f"{prefix}字第{number}号"

#############################其他常见类型###########################################

    # 1、随机整数-可变长整数-限制长度50以内
    @staticmethod
    def get_number(length=None):
        if length:
            list1 = [str(i) for i in range(1, 10)] * 5
            str_num = ''.join(random.sample(list1, length))
            return str_num
        else:
            return random.randint(1, 10000)

    # 2、随机-或指定长度-字符串
    @staticmethod
    def get_character(length=None):
        if length:
            return fake.pystr(min_chars=None, max_chars=length)
        else:
            return fake.pystr(min_chars=None, max_chars=None)

    # 3、文章--限制长度500以内
    @staticmethod
    def get_description(length=None):
        if length:
            long = fake.paragraph(nb_sentences=100, variable_nb_sentences=True, ext_word_list=None)
            return long[:length]
        else:
            long = fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
            return long

    # 6、文章-含换行符
    @staticmethod
    def get_change_line_description():
        return fake.text(max_nb_chars=50, ext_word_list=None).replace('.','\n')

    # 7、时间-创建时间
    @staticmethod
    def get_create_time():
        return str(datetime.datetime.now()).split('.')[0]

    # 8、时间-更新时间
    @staticmethod
    def get_update_time():
        return str(datetime.datetime.now()).split('.')[0]

    # 9、时间-时间戳
    @staticmethod
    def get_timestamp():
        return str(time.time()*1000).split('.')[0]

    # 职位
    @staticmethod
    def get_job():
        return fake.job()

    # 完整信用卡信息
    @staticmethod
    def get_full_credit_card():
        return fake.credit_card_full(card_type=None)

    # 年月日
    @staticmethod
    def get_date():
        return fake.date(pattern="%Y-%m-%d", end_datetime=None)

    # 年
    @staticmethod
    def get_year():
        return fake.year()
        # return 1963

    # 月
    @staticmethod
    def get_month():
        return fake.month()

    # 日
    @staticmethod
    def get_day():
        return fake.day_of_month()

    # 周几
    @staticmethod
    def get_weekday():
        return fake.day_of_week()

    # 时间 时分秒
    @staticmethod
    def get_time():
        return fake.time(pattern="%H:%M:%S", end_datetime=None)

    # 时区
    @staticmethod
    def get_timezone():
        return fake.timezone()

    # 国家名称
    @staticmethod
    def get_country():
        return fake.country()

    # 省份
    @staticmethod
    def get_province():
        return fake.province()

    # 街道
    @staticmethod
    def get_street():
        return fake.street_address()

    # 颜色名称
    @staticmethod
    def get_color():
        return fake.color_name()

    # 颜色十六进制值
    @staticmethod
    def get_hex_color():
        return fake.hex_color()

    # 颜色十六进制值
    @staticmethod
    def get_file_name():
        return fake.file_name()

    # 文件路径
    @staticmethod
    def get_file_path():
        return fake.file_path(depth=3, category=None, extension=None)

    # 主机名
    @staticmethod
    def get_hostname():
        return fake.hostname()

    # url
    @staticmethod
    def get_url():
        return fake.url(schemes=None)

    # 图片url
    @staticmethod
    def get_image_url():
        return fake.image_url(width=None, height=None)

    # ipv4
    @staticmethod
    def get_ipv4():
        return fake.ipv4(network=False, address_class=None, private=None)

    # ipv6
    @staticmethod
    def get_ipv6():
        return fake.ipv6(network=False)

    # mac
    @staticmethod
    def get_mac_address():
        return fake.mac_address()

    # 用户名
    @staticmethod
    def get_user_name():
        return fake.user_name()

    # 二进制--暂固定20位
    @staticmethod
    def get_binary():
        return fake.binary(length=20)

    # 布尔值
    @staticmethod
    def get_boolean():
        return fake.boolean(chance_of_getting_true=50)

    # NULL+布尔值
    @staticmethod
    def get_null_boolean():
        return fake.null_boolean()

    # 密码
    @staticmethod
    def get_password():
        return fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

    # md5
    @staticmethod
    def get_md5():
        return fake.md5(raw_output=False)

    # sha1
    @staticmethod
    def get_sha1():
        return fake.sha1(raw_output=False)

    # sha256
    @staticmethod
    def get_sha256():
        return fake.sha256(raw_output=False)

    # 档案(完整)--字典
    @staticmethod
    def get_profile():
        return fake.profile(fields=None, sex=None)

    # 档案(简单)--字典
    @staticmethod
    def get_simple_profile():
        return fake.simple_profile(sex=None)

    # 字典
    @staticmethod
    def get_dictionary():
        return fake.pydict(nb_elements=5, variable_nb_elements=True)

    # 列表
    @staticmethod
    def get_list():
        return fake.pylist(nb_elements=5, variable_nb_elements=True)

    # 集合
    @staticmethod
    def get_set():
        return fake.pyset(nb_elements=5, variable_nb_elements=True)

    # 元组
    @staticmethod
    def get_tuple():
        return fake.pytuple(nb_elements=5, variable_nb_elements=True)

    # 嵌套结构数据
    @staticmethod
    def get_struct():
        return fake.pystruct(count=10)

    # 几位小数--小于等于14
    @staticmethod
    def get_float(length=None):
        if length:
            if int(length) > 14:
                raise ValueError("wrong length: it should be smaller than 15...")
            return fake.pyfloat(left_digits=None, right_digits=length, positive=True, min_value=None, max_value=None)
        return fake.pyfloat(left_digits=None, right_digits=None, positive=True, min_value=None, max_value=None)

    # 随机浏览器代理信息
    @staticmethod
    def get_user_agent():
        return fake.user_agent()

    # 特殊字符串--长度小于22-list长度；
    @classmethod
    def get_special_character(cls, length=None):
        if length:
            return ''.join(random.sample(cls._SPECIAL_CHARACTERS, length))
        return ''.join(random.sample(cls._SPECIAL_CHARACTERS, 7))

    # 011、少数民族姓名
    @classmethod
    def get_special_name(cls):
        return random.choice(cls._MINORITY_NAMES)

    @staticmethod
    def get_uuid():
        return fake.uuid4()

###################### 固定正则匹配数据 ############################

    # 正则一、

    # 正则二、

    # 正则三、

######################## 非隐私类型 ####################################

    # 1、空值
    @staticmethod
    def get_null_value1():
        return 'null'

    @staticmethod
    def get_null_value2():
        return ''

    @staticmethod
    def get_null_value3():
        return ' '

    # 2、其他
    @classmethod
    def get_uid(cls):
        return cls.get_number(7)

##########################  ############################


fake.add_provider(MyProvider)


base_list1 = ['address', 'bank_card', 'email', 'company_name', 'enterprise_name', 'name', 'id_no', 'id_card', 'phone', 'phone_number', 'fix_phone', 'post_code', 'car_no', 'social_credit_code', 'car_code', 'passport', 'tax_code', 'organization', 'enterprise_code', 'individual_business', 'officer_card']

class MockMysqlData:

    @staticmethod
    # 生成获取columns的mysql语句
    def get_columns(dbname, table_name):
        return f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table_name}';"

    @staticmethod
    # 生成单条sql插入的语句
    def single_sql(table_name, column_list):
        data1 = [getattr(fake, f'get_{i.lower()}')() for i in column_list]
        col1 = ','.join(column_list)
        new_col = f'({col1})'
        return f"insert into {table_name} {new_col} values {tuple(data1)};"

    @staticmethod
    def many_sql(table_name, column_list, number, start_index):
        data_list = []
        for i in range(int(number)):
            data1 = [getattr(fake, ('get_'+j.lower()))() for j in column_list]
            data1[0] = i + int(start_index) + 1
            data_list.append(tuple(data1))
        values_format = ','.join(['%s'] * len(column_list))
        values_format = f'({values_format})'
        columns_format = f"({','.join(column_list)})"
        sql2 = f"insert into {table_name} {columns_format} values {values_format}"
        return [sql2, data_list]

    # 暂未测试
    @staticmethod
    def load_file_data(table_name, column_list, numbers):
        col1 = ','.join(column_list)
        new_col = f'({col1})'
        sql3 = f"load data infile './data.txt' into table {table_name} {new_col};"
        with open(r'./data.txt', 'w+') as f:
            for i in range(int(numbers)):
                data1 = [getattr(fake, i)() for i in column_list]
                data1[0] = i + 102
                new_data1 = (str(tuple(data1))).strip('(').strip(')')
                f.write(new_data1+'\n')
        return sql3


class MockOracleData:

    @staticmethod
    def insert_one_contains_index(table_name, columns_list, start_index):
        data1 = [getattr(fake, f'get_{j.lower()}')() for j in columns_list]
        data1[0] = int(start_index) + 1
        col1 = ','.join(columns_list)
        new_col = f'({col1})'
        return f"insert into {table_name} {new_col} values {tuple(data1)}"

    @staticmethod
    def insert_one(table_name, columns_list):
        data1 = [getattr(fake, f'get_{j.lower()}')() for j in columns_list]
        col1 = ','.join(columns_list)
        new_col = f'({col1})'
        return f"insert into {table_name} {new_col} values {tuple(data1)}"

    @staticmethod
    def insert_many(table_name, columns_list, start_index, number):
        columns_format = f"({','.join(columns_list)})"
        sql2 = "insert all"
        for i in range(int(number)):
            data1 = [getattr(fake, f'get_{j.lower()}')() for j in columns_list]
            data1[0] = int(start_index) + 1 + i
            sql2 += f'\ninto {table_name} {columns_format}  values {tuple(data1)}'
        sql2 += '\n'
        sql2 += "SELECT 1 from dual"

        return sql2

    @staticmethod
    def get_columns(table_name):
        return f"SELECT wm_concat(T.COLUMN_NAME) as cols FROM USER_TAB_COLUMNS T WHERE T.TABLE_NAME = '{table_name}'"

    @staticmethod
    def one_column_data(column_name, number):
        data_list = []
        for i in range(number):
            new_data = getattr(fake, column_name)
            data_list.append(new_data)
        return data_list


# hive-这里不能带';'
class MockMyhiveData:

    @staticmethod
    # 生成获取columns的mysql语句
    def get_columns(dbname, table_name):
        return f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table_name}'"

    @staticmethod
    # 生成单条sql插入的语句
    def single_sql(table_name, column_list):
        data1 = [getattr(fake, f'get_{i.lower()}')() for i in column_list]
        col1 = ','.join(column_list)
        new_col = f'({col1})'
        return f"insert into {table_name} {new_col} values {tuple(data1)}"


if __name__ == '__main__':
    # 1、新建mock
    # new_mock = MockMyhiveData()
    new_mock = MockOracleData()

    # 2、新建连接
    # new_presto_connect = MySql(host='192.168.7.240',sql_type='presto')
    if MySql:
        new_oracle_connect = MySql(host='192.168.9.215', port=1521, user='TESTOR', passwd='123456', sample='XE', sql_type='oracle')
        # new_mysql_connect = MySql(host='192.168.7.241', port=3306, user='root', passwd='123456', dbname='autotest1', sql_type='mysql')

    # 3、提供表名 和 列
    table_name = 'autotest1.all_private_table3'
    column_list_new = ['uuid', 'name', 'phone_number', 'id_no', 'address', 'bank_card', 'company_name', 'job', 'email', 'post_code', 'car_no', 'social_credit_code', 'car_code', 'passport', 'tax_code', 'organization', 'enterprise_code', 'individual_business', 'officer_card']
    # column_list_new = ['uuid','name','optional_name','address','phone','company']
    # # 4-1、只造数据、写入文件
    # with open(r'sql_temp001','w',encoding='utf-8') as f:
    #     for i in range(10):
    #         sql001 = new_mock.single_sql(table_name=table_name, column_list=column_list_new)
    #         f.write(sql001.replace('\u2022','')+'\n')

    # 4-2、直接连接sql并插入数据
    t1 = time.time()
    if MySql and 'new_presto_connect' in locals():
        for i in range(1000):
            sql001 = new_mock.single_sql(table_name=table_name, column_list=column_list_new)
            new_presto_connect.get_data_hive(sql001)
            # new_presto_connect.execute_sql(sql001)
            new_presto_connect.commit()
        t2 = time.time()

        # # 5、末尾-关闭连接
        new_presto_connect.close()
        print(t2-t1)


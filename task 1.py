#Задание 1.
#Условие:
#Переделать все шаги позитивных тестов на выполнение по SSH. Проверить работу.

import subprocess

import yaml

from sshcheckers import upload_files, ssh_checkout, ssh_getout

with open("config.yaml") as f:
    data = yaml.safe_load(f)


def test_step0():
    """Деплой"""
    res = []
    upload_files(data["host"], data["user"], "123",
                 f"{data['local_path']}/p7zip-full.deb",
                 f"{data['remote_path']}/p7zip-full.deb")
    res.append(ssh_checkout(data["host"], data["user"], "123",
                            f"echo '123' | sudo -S dpkg -i {data['remote_path']}/p7zip-full.deb",
                            "Настраивается пакет"))
    res.append(ssh_checkout(data["host"], data["user"], "123", "echo '123' | sudo -S dpkg -s p7zip-full",
                            "Status: install ok installed"))
    assert all(res), "Deploy FAIL"


def test_step1(make_folders, clear_folders, make_files):
    """Создание архива и проверка его наличия в директории out"""
    res1 = ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_in"]}; '
                        f'7z a -t{data["arc_type"]} {data["folder_out"]}/arx1.{data["arc_type"]}',
                        "Everything is Ok")
    res2 = ssh_checkout(data["host"], data["user"], "123",
                        f'ls {data["folder_out"]}',
                        f'arx1.{data["arc_type"]}')
    assert res1 and res2, 'Test 1 FAIL'


def test_step2(clear_folders, make_files):
    """Разархивация архива в директорию и проверка наличия там файлов из архива"""
    res = []
    res.append(ssh_checkout(data["host"], data["user"], "123",
                            f'cd {data["folder_in"]}; '
                            f'7z a -t{data["arc_type"]} {data["folder_out"]}/arx1.{data["arc_type"]}',
                            'Everything is Ok'))
    res.append(ssh_checkout(data["host"], data["user"], "123",
                            f'cd {data["folder_out"]}; 7z e arx1.{data["arc_type"]} -o{data["folder_ext"]} -y',
                            'Everything is Ok'))
    for item in make_files:
        res.append(ssh_checkout(data["host"], data["user"], "123",
                                f'ls {data["folder_ext"]}',
                                item))
    assert all(res), 'Test2 FAIL'


def test_step3():
    """Проверка целостности архива"""
    assert ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_in"]}; 7z t {data["folder_out"]}/arx1.{data["arc_type"]}',
                        'Everything is Ok'), 'Test 3 FAIL'


def test_step4():
    """Проверка возможности обновления архива"""
    assert ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_in"]}; 7z u {data["folder_out"]}/arx1.{data["arc_type"]}',
                        'Everything is Ok'), 'Test 4 FAIL'


def test_step5(clear_folders, make_files):
    """Проверка удаления содержимого архива arx2"""
    res = []
    res.append(
        ssh_checkout(data["host"], data["user"], "123",
                     f'cd {data["folder_in"]}; '
                     f'7z a -t{data["arc_type"]} {data["folder_out"]}/arx1.{data["arc_type"]}',
                     "Everything is Ok"))
    for item in make_files:
        res.append(ssh_checkout(data["host"], data["user"], "123",
                                f'cd {data["folder_out"]}; 7z l arx1.{data["arc_type"]}',
                                item))
    assert all(res), 'Test 5 FAIL'


def test_step6(clear_folders, make_files, make_subfolder):
    """Проверка разархивирования файлов с сохранением структуры директорий (x)
        и команды вывода списка файлов (l) в архиве"""
    ssh_checkout(data["host"], data["user"], "123",
                 f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx1.{data["arc_type"]}',
                 "")
    res = []
    res.append(ssh_checkout(data["host"], data["user"], "123",
                            f'cd {data["folder_out"]}; 7z x arx1.{data["arc_type"]} -o{data["folder_ext"]} -y',
                            "Everything is Ok"))
    for item in make_files:
        res.append(ssh_checkout(data["host"], data["user"], "123",
                                f'cd {data["folder_out"]}; 7z l arx1.{data["arc_type"]}',
                                item))
        res.append(ssh_checkout(data["host"], data["user"], "123",
                                f'ls {data["folder_ext"]}',
                                item))
    res.append(ssh_checkout(data["host"], data["user"], "123",
                            f'ls {data["folder_ext"]}',
                            make_subfolder[0]))
    res.append(ssh_checkout(data["host"], data["user"], "123",
                            f'cd {data["folder_ext"]}/{make_subfolder[0]}; ls',
                            make_subfolder[1]))
    print(res)
    assert all(res), 'test 6 FAIL'


def test_step7():
    """Очистка содержимое архива arx1"""
    assert ssh_checkout(data["host"], data["user"], "123",
                        f'7z d {data["folder_out"]}/arx1.{data["arc_type"]}',
                        'Everything is Ok'), 'Test 7 FAIL'


def test_step8(make_folders, clear_folders, make_files):
    """Тестирование команды расчёта хэша"""
    sb = subprocess.run(f'cd {data["folder_out"]}; crc32 arx1.{data["arc_type"]}',
                        shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    arc_hash = sb.stdout[:-1].upper()
    ssh_checkout(data["host"], data["user"], "123",
                 f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx1.{data["arc_type"]}',
                 "")
    assert ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_out"]}; 7z h arx1.{data["arc_type"]}', arc_hash), 'test 8 FAIL'
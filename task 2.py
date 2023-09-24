import yaml

from sshcheckers import ssh_checkout_negative, upload_files

with open("config.yaml") as f:
    data = yaml.safe_load(f)


def test_step0():
    """Деплой"""
    res = []
    upload_files(data["host"], data["user"], "123",
                 f"{data['local_path']}/p7zip-full.deb",
                 f"{data['remote_path']}/p7zip-full.deb")
    res.append(ssh_checkout_negative(data["host"], data["user"], "123",
                                     f"echo '123' | sudo -S dpkg -i {data['remote_path']}/p7zip-ful.deb",
                                     "Нет такого файла или каталога"))
    res.append(ssh_checkout_negative(data["host"], data["user"], "123", "echo '123' | sudo -S dpkg -s p7zip-ful",
                                     "не установлен"))
    assert all(res), "Deploy FAIL"


def test_step1(clear_folders, make_folders, make_files, make_bad_arx):
    """Разархивируем архив в директорию и проверяем наличие там файлов"""
    assert ssh_checkout_negative(data["host"], data["user"], "123",
                                 f'cd {data["folder_out"]}; 7z e badarx.{data["arc_type"]} -o{data["folder_ext"]} -y',
                                 "ERROR"), 'Test 1 (neg) FAIL'


def test_step2(clear_folders, make_folders, make_files, make_bad_arx):
    """Проверяем целостность архива"""
    assert ssh_checkout_negative(data["host"], data["user"], "123",
                                 f'cd {data["folder_out"]}; 7z t badarx.{data["arc_type"]}',
                                 "ERROR"), 'Test 2 (neg) FAIL'


def test_step3(clear_folders, make_folders, make_files, make_bad_arx):
    """Создание архива с несуществующим расширением"""
    assert ssh_checkout_negative(data["host"], data["user"], "123",
                                 f'cd {data["folder_in"]}; '
                                 f'7z a -t{data["bad_arc_type"]} {data["folder_out"]}/arx1.{data["bad_arc_type"]}',
                                 "Unsupported archive type"), 'Test 3 (neg) FAIL'
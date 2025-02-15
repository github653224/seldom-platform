"""
author: @bugmaster
date: 2022-02-07
function: 项目管理
"""
import os
import hashlib
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from ninja import Router
from ninja import File
from ninja.files import UploadedFile
from utils.response import response, Error
from seldom import SeldomTestLoader
from seldom import TestMainExtend
from ninja import Schema
from app_project.models import Project
from app_case.models import TestCase
from backend.settings import BASE_DIR

# upload image
IMAGE_DIR = os.path.join(BASE_DIR, "static", "images")

router = Router(tags=["project"])


class ProjectItems(Schema):
    name: str
    address: str
    cover_name: str
    path_name: str


@router.post('/create')
def create_project(request, project: ProjectItems):
    """
    创建项目
    """
    project_obj = Project.objects.create(
        name=project.name, address=project.address)
    return response(data=model_to_dict(project_obj))


@router.get('/list')
def get_projects(request):
    """
    获取项目列表
    """
    projects = Project.objects.filter(is_delete=False)
    project_list = []
    for project in projects:
        project_list.append(model_to_dict(project))
    return response(data=project_list)


@router.get('/{project_id}/')
def get_project(request, project_id: int):
    """
    通过项目ID查询项目
    """
    project_obj = get_object_or_404(Project, pk=project_id, is_delete=False)
    return response(data=model_to_dict(project_obj))


@router.put('/{project_id}/')
def update_project(request, project_id: int, project: ProjectItems):
    """
    通过项目ID更新项目
    """
    project_obj = get_object_or_404(Project, pk=project_id)
    project_obj.name = project.name
    project_obj.address = project.address
    project_obj.cover_name = project.cover_name
    project_obj.path_name = project.path_name
    project_obj.save()
    return response(data=model_to_dict(project_obj))


@router.delete('/{project_id}/')
def delete_project(request, project_id: int):
    """
    通过项目ID删除项目
    """
    project_obj = get_object_or_404(Project, pk=project_id)
    project_obj.is_delete = True
    project_obj.save()
    return response()


@router.post("/upload", auth=None)
def upload_project_image(request, file: UploadedFile = File(...)):
    """
    项目图片上传
    """
    # 判断文件后缀名
    suffix = file.name.split(".")[-1]
    if suffix not in ["png", "jpg", "jpeg", "gif"]:
        return response(error=Error.FILE_TYPE_ERROR)

    # 判断文件大小 1024 * 1024 * 2 = 2MB
    if file.size > 2097152:
        return response(error=Error.FILE_SIZE_ERROR)

    # 文件名生成md5
    file_md5 = hashlib.md5(bytes(file.name, encoding="utf8")).hexdigest()
    file_name = file_md5 + "." + suffix

    # 保存到本地
    upload_file = os.path.join(IMAGE_DIR, file_name)
    with open(upload_file, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)

    return response(data={"name": file_name})


# @router.put("/cover/remove/{project_id}/", auth=None)
# def remove_project_image(request, project_id: int):
#     """
#     后续有具体删除需求备用
#     项目图片删除
#     """
#     project_obj = get_object_or_404(Project, pk=project_id)
#     project_obj.cover_name = ""
#     project_obj.path_name = ""
#     project_obj.save()
#     return response()


@router.get("/{project_id}/sync")
def update_project_cases(request, project_id: int):
    """
    同步项目用例
    """
    project_obj = get_object_or_404(Project, pk=project_id)
    # 项目本地目录
    test_dir = os.path.join(project_obj.address, "test_dir")
    # 开启收集测试用例
    SeldomTestLoader.collectCaseInfo = True
    # 收集测试用例信息
    main_extend = TestMainExtend(path=test_dir)
    seldom_case = main_extend.collect_cases()
    platform_case = TestCase.objects.filter(project=project_obj)
    # project_case.delete()

    # 从seldom项目中找到新增的用例
    for seldom in seldom_case:
        for platform in platform_case:
            if (seldom["file"] == platform.file_name
                    and seldom["class"]["name"] == platform.class_name
                    and seldom["method"]["name"] == platform.case_name):
                break
        else:
            TestCase.objects.create(
                project_id=project_id,
                file_name=seldom["file"],
                class_name=seldom["class"]["name"],
                class_doc=seldom["class"]["doc"],
                case_name=seldom["method"]["name"],
                case_doc=seldom["method"]["doc"],
            )

    # 从platform找出已删除的用例
    for platform in platform_case:
        for seldom in seldom_case:
            if (platform.file_name == seldom["file"]
                    and platform.class_name == seldom["class"]["name"]
                    and platform.case_name == seldom["method"]["name"]):
                break
        else:
            test_case = TestCase.objects.filter(project=project_obj, id=platform.id)
            test_case.delete()

    return response()


@router.get("/{project_id}/files")
def get_project_files(request, project_id: int):
    """
    获取项目用例文件列表
    """
    cases = TestCase.objects.filter(project_id=project_id)
    case_number = len(cases)
    files = []
    files_name = []
    for case in cases:
        if "." in case.file_name:
            case_path = case.file_name.split('.')
        else:
            case_path = [case.file_name + ".py"]

        if case_path[0] not in files_name:
            files_name.append(case_path[0])
            if ".py" in case_path[0]:
                case_level_one = {
                    "label": case_path[0],
                    "full_name": case_path[0],
                    "is_leaf": 1,
                    "children": []
                }
            else:
                case_level_one = {
                    "label": case_path[0],
                    "full_name": case_path[0],
                    "is_leaf": 0,
                    "children": []
                }

            files.append(case_level_one)

    return response(data={"case_number": case_number, "files": files})


@router.get('/{project_id}/cases')
def get_project_file_cases(request, project_id: int, file_name: str):
    """
    获取文件下面的测试用例
    """
    # 如果是文件，直接取文件的类、方法
    if ".py" in file_name:
        file_cases = TestCase.objects.filter(
            project_id=project_id,
            file_name=file_name[0:-3]
        )
        case_list = []
        for case in file_cases:
            case_list.append(model_to_dict(case))
        # 通过接口返回
        return response(data=case_list)
    else:
        return response(data=[])


@router.get('/{project_id}/subdirectory')
def get_project_subdirectory(request, project_id: int, file_name: str):
    """
    获取子目录
    """
    all_cases = TestCase.objects.filter(project_id=project_id)
    files_name = []
    for case in all_cases:
        if case.file_name.startswith(file_name + ".") is True:
            if case.file_name[len(file_name + "."):] not in files_name:
                files_name.append(case.file_name[len(file_name + "."):])

    case_name = []
    dir_name = []
    for f_name in files_name:
        if "." in f_name:
            case_path = f_name.split('.')
            if case_path[0] not in dir_name:
                dir_name.append(case_path[0])
            else:
                continue
            case_level_two = {
                "label": case_path[0],
                "full_name": file_name + "." + case_path[0],
                "is_leaf": 0,
                "children": []
            }
        else:
            case_path = [f_name + ".py"]
            case_level_two = {
                "label": case_path[0],
                "full_name": file_name + "." + case_path[0],
                "is_leaf": 1,
                "children": []
            }
        case_name.append(case_level_two)

    return response(data=case_name)

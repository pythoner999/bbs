"""
bbs用到的form類
"""

from django import forms
from django.core.exceptions import ValidationError
from blog import models


# 定義一個註冊的form類
class RegForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        label="用戶名",
        error_messages={
            "max_length": "用戶名最長16位",
            "required": "用戶名不能為空",
        },

        widget=forms.widgets.TextInput(
            attrs={"class": "form-control"},
        )
    )

    password = forms.CharField(
        min_length=6,
        label="密碼",
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control"},
            render_value=True,
        ),
        error_messages={
            "min_length": "密碼至少要6位",
            "required": "密碼不能為空",
        }
    )

    re_password = forms.CharField(
        min_length=6,
        label="確認密碼",
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control"},
            render_value=True,
        ),
        error_messages={
            "min_length": "確認密碼至少要6位！",
            "required": "確認密碼不能為空",
        }
    )

    email = forms.EmailField(
        label="郵箱",
        widget=forms.widgets.EmailInput(
            attrs={"class": "form-control"},

        ),
        error_messages={
            "invalid": "郵箱格式不正確",
            "required": "郵箱不能為空",
        }
    )

    # 重寫username字段的局部鉤子
    def clean_username(self):
        username = self.cleaned_data.get("username")
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            # 表示用戶名已被註冊
            self.add_error("username", ValidationError("用戶名已經存在！"))
        else:
            return username

    # 重寫email字段的局部鉤子
    def clean_email(self):
        email = self.cleaned_data.get("email")
        is_exist = models.UserInfo.objects.filter(email=email)
        if is_exist:
            # 表示郵箱已被註冊
            self.add_error("email", ValidationError("郵箱已被註冊"))
        else:
            return email

    # 重寫全局的鉤子，對確認密碼做校驗
    def clean(self):
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")

        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("兩次密碼不一致"))

        else:

            return self.cleaned_data

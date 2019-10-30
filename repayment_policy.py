"""
Repayment Policy version constant

Instead of using a simple collection of strings, it is defined in OOP style such that multiple info and related methods
can be added.

Basic format of the repayment policy:
    RepaymentPolicy -> Type -> Version
Each version has a code in the form of `{Type number}.{Version number}` (e.g. `2.1`)

Objective of this constant implementation is to reduce errors for whom using this code
    - Since it is a constant, everything is implemented to be used as a class instance instead of an object instance
        - if used it as an object instance (x) -> RepaymentPolicy().type1().v1()
        - if used it as a class instance (o) -> RepaymentPolicy.type1.v1
    - To maximize IDE's auto complete heaven, all class attributes are explicitly declared
"""
from typing import Tuple
from static_attr_object import StaticAttrObject


class _RepaymentPolicyVersionBase(StaticAttrObject):
    """상환 정책 버전 정보 base class

    추후 version 과 관련된 정보를 저장해서 사용할 일이 있을 때를 대비해 class 로 설정 (예: 정책 적용 시작일)

    Attributes:
        version_number (int): 정책 버전 숫자
    """
    version_number = None

    def __init__(self, **kwargs):
        # init 을 추가하지 않으면 이유는 알 수 없지만 attribute docstring 에 unresolved reference 가 발생
        super().__init__(**kwargs)


class _RepaymentPolicyTypeMetaClass(type):
    """상환 타입 meta class
    """
    def __getattribute__(self, item):
        """특정 상환 버전을 호출할 때 상환정책 version 코드를 build 해서 리턴시킨다 (예: `2.1`)
        """
        mapped_item_name = f'_{item}'
        try:
            mapped_item = super().__getattribute__(mapped_item_name)
            if isinstance(mapped_item, _RepaymentPolicyVersionBase):
                return f'{self.type_number}.{mapped_item.version_number}'
        except AttributeError:
            pass

        return super().__getattribute__(item)


class _RepaymentPolicyTypeBase(StaticAttrObject, metaclass=_RepaymentPolicyTypeMetaClass):
    type_number = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def _get_version_attr_names(cls):
        """이 상환 타입에서 _RepaymentPolicyVersionBase 타입의 object 를 값으로 들고 있는 (version) attribute 들의 이름을 리턴한다.

        version attribute 들은 이름이 v{숫자}로 구성되어 있다 (예: v1).

        Returns:
            tuple(str): _RepaymentPolicyVersionBase 타입을 값으로 들고 있는 attribute 이름들
        """
        return (attr_name for attr_name in cls._get_attr_names() if attr_name.startswith('v'))

    @classmethod
    def is_in_type(cls, checking_version: str) -> bool:
        """checking_version 의 상환정책 version 이 이 상환타입에 속해있는지 확인한다

        Args:
            checking_version: 상환정책 version

        Returns:
            이 타입에 속한 상환정책 version 이면 True
        """
        version_token = checking_version.split('.')
        if len(version_token) != 2:
            raise ValueError("알 수 없는 상환정책 version입니다.")
        else:
            return cls.type_number == int(version_token[0])


class _RepaymentPolicyType1(_RepaymentPolicyTypeBase):
    """상환 정책 타입 1

    타입 1 공통 내역:
        - ...

    Attributes:
        v1 (_RepaymentPolicyVersionBase):
            - ...
        v2 (_RepaymentPolicyVersionBase):
            - ...
    """
    type_number = 1
    _v1 = _RepaymentPolicyVersionBase(version_number=1)
    _v2 = _RepaymentPolicyVersionBase(version_number=2)
    # private attribute 를 이용해서 자동으로 상환정책 version code 를 할당한다 (예: 2.1)
    v1 = None
    v2 = None

    def __init__(self, **kwargs):
        # init 을 추가하지 않으면 이유는 알 수 없지만 attribute docstring 에 unresolved reference 가 발생
        super().__init__(**kwargs)


class _RepaymentPolicyType2(_RepaymentPolicyTypeBase):
    """상환 정책 타입 2

    타입 2 공통 내역:
        - ...

    Attributes:
        v1 (_RepaymentPolicyVersionBase):
            - ...
    """
    type_number = 2
    _v1 = _RepaymentPolicyVersionBase(version_number=1)
    # private attribute 를 이용해서 자동으로 상환정책 version code 를 할당한다 (예: 2.1)
    v1 = None

    def __init__(self, **kwargs):
        # init 을 추가하지 않으면 이유는 알 수 없지만 attribute docstring 에 unresolved reference 가 발생
        super().__init__(**kwargs)


class RepaymentPolicy(StaticAttrObject):
    """상환 정책 버전 class

    상환정책은 type -> version 으로 나뉘며, type 은 이자의 계산일이 같은 종류를 표현하고, version 은 같은 type 중 세부적으로 다른 내용이 있는 경우
    추가된다. 정책의 자세한 내용은 각 type class 참조
    """
    type1 = _RepaymentPolicyType1
    type2 = _RepaymentPolicyType2

    @classmethod
    def get_all_versions(cls) -> Tuple[str]:
        """현재 사용 가능한 모든 상환 정책 버전 코드를 리턴한다.

        Returns:
            모든 상환 정책 버전 코드
        """
        version_codes = []
        type_names = [attr_name for attr_name in cls._get_attr_names() if attr_name.startswith('type')]
        for type_name in type_names:
            cur_type = getattr(cls, type_name)
            for version_name in cur_type._get_version_attr_names():
                cur_version = getattr(cur_type, version_name)
                version_codes.append(cur_version)

        return tuple(sorted(version_codes))

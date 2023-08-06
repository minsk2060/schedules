# ��� �������� ���������
# ������� �������-��������� select
# � �������� � ��� � �������� ��������� ������ ������� foo
def select(foo):
    # ������� base() ������� ������ ����������, ������� ����� ������������
    # ���� ������� foo()
    def base():
        print("######")
        foo() # �������� ��� �� ��� ����, ��� ����� �������
        print("######")
    return base


# ������� ����� ������� hello() � ��������� � ��� ���������
# (�.�. �������� � � �������� ��������� � �������-���������)
@select
def hello():
    print("------")


# ������� ����� �������, � ������� �������� ���������,
# �� �� ����� ���������� �������� ���������, � ������� ���� ����� �������
hello()

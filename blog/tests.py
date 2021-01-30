from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User


# Create your tests here.
# TDD개발! -> 브라우저를 직접 열어서 동작을 확인하지 않아도, 오류를 확인 가능, 또한 리팩토링 과정 중에서도 테스트를 지속적으로 수행함으로 오류 여부를 확인 가능하다.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()  # 이 클라이언트가 브라우저 역할을 대신 해줄 것임
        self.auther_000 = User.objects.create(username = 'smith', password = 'nopassword')  # 새로운 포트스 생성을 위해 user를 생성해줌.

    def test_post_list(self):   #함수 이름에 'test_'는 약속(필수)임 -> 오류 가능성도 있음
        response = self.client.get('/blog/')    #클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200) # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명

        soup = BeautifulSoup(response.content, 'html.parser')   # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함


        title = soup.title          # 이렇게 하면 해당 소스의 title을 바로 가져올 수 있다.

        #print(title)    # -> 태그 포함 출력
        #print(title.text)   # 사람이 보는 것과 같이 태그 제외하고 출력

        self.assertEqual(title.text, 'Blog')    # 타이틀이 Blog인지 테스트
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        self.assertEqual(Post.objects.count(), 0)   # db 명령 (get, all 과 같은 것) -> 테스트 코드 내에서 아직 포스트를 생성하지 않았기때문에 포스트의 개수는 0이다.
        self.assertIn('아직 게시물이 없습니다.', soup.body.text)  #포스트 0개이기 때문에 html 내에서 아직 게시물이 없습니다. 가 동작하고, 따라서 테스트도 통과한다.


        post_000 = Post.objects.create(             #포스트 생성! -> 테스트는 db를 제로베이스에서 실행하기 때문에 브라우저 상황과는 관계 없이 새로 생성해야함.
            title = "Example",
            content = "Hi",
            created = timezone.now(),
            author = self.auther_000,
        )
        self.assertGreater(Post.objects.count(), 0)     #0개보다 많으면 통과

        response = self.client.get('/blog/')    #클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200) # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명
        soup = BeautifulSoup(response.content, 'html.parser')   # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다.', body.text)    # 게시물이 하나 있기 때문에 이게 출력 안됨,, 따라서 테스트 통과함(notin!!)
        self.assertIn(post_000.title, body.text)

        
       
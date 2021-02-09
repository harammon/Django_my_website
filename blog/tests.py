from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone

from .models import Post, Category, Tag, Comment


def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(name=name, description=description)  # category가 없을 경우 새로 생성되고, is_created 는 True가 전달된다.

    # slug 위해 추가되는 코드!

    category.slug = category.name.replace(' ', '-').replace('/', '')
    category.save()     # 바뀐 slug가 save됨

    return category

def create_tag(name='some tag'):
    tag, is_created = Tag.objects.get_or_create(name = name)
    tag.slug = tag.name.replace(' ', '-').replace('/', '')
    tag.save()

    return tag



def create_comment(post, text='a comment', author = None):
    if author is None:
        author, is_created = User.objects.get_or_create(
            username = 'guest',
            password = 'guestpassword'
        )
    comment = Comment.objects.create(
        post = post,
        text = text,
        author =author
    )

    return comment

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(  # 포스트 생성함수! -> 테스트 함수는 db를 제로베이스에서 실행하기 때문에 브라우저 상황과는 관계 없이 새로 생성해야함.
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category,
    )
    return blog_post


# 카테고리 연결 위한 테스트 클래스
class TestModel(TestCase):
    def setUp(self):
        self.client = Client()  # 이 클라이언트가 브라우저 역할을 대신 해줄 것임
        self.author_000 = User.objects.create_user(username='smith', password='nopassword')  # 새로운 포트스 생성을 위해 user를 생성해줌.

    def test_category(self):
        category = create_category()
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
            category=category
        )
        self.assertEqual(category.post_set.count(), 1)      #외래키로 등록되어 있기 때문에, 카테고리 객체에서 post를 불러올 수 있다.
        # 이 때의 함수는 클래스 명을 소문자로 하여 접근 가능하다.
    #_set : 자신이 속해 있는 _ 앞에 있는 것을 가져올 수 있음!! -> 추가 검색 요망
    def test_tag(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title="Stay Fool",
            content="Story about Jobs",
            author=self.author_000,
        )
        post_001.tags.add(tag_001)
        post_001.save()

        self.assertEqual(post_000.tags.count(), 2)# post는 여러 개의 tag를 가질 수 있다.
        self.assertEqual(tag_001.post_set.count(), 2)# 하나의 tag는 여러 개의 post에 붙을 수 있다.
        self.assertEqual(tag_001.post_set.first(), post_000)# 하나의 tag는 자신을 가진 post들을 불러올 수 있다.
        self.assertEqual(tag_001.post_set.last(), post_001)  # 하나의 tag는 자신을 가진 post들을 불러올 수 있다.

    def test_post(self):
        # 포스트 생성! -> 테스트는 db를 제로베이스에서 실행하기 때문에 브라우저 상황과는 관계 없이 새로 생성해야함.
        category = create_category()
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
            category=category
        )

    def test_comment(self):
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )
        self.assertEqual(Comment.objects.count(), 0)

        comment_000 = create_comment(
            post = post_000
        )
        comment_001 = create_comment(
            post=post_000,
            text = 'second comment'
        )

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)



# Create your tests here.
# TDD개발! -> 브라우저를 직접 열어서 동작을 확인하지 않아도, 오류를 확인 가능, 또한 리팩토링 과정 중에서도 테스트를 지속적으로 수행함으로 오류 여부를 확인 가능하다.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()  # 이 클라이언트가 브라우저 역할을 대신 해줄 것임
        self.author_000 = User.objects.create_user(username='smith', password='nopassword')  # 새로운 포트스 생성을 위해 user를 생성해줌.
        self.user_obama = User.objects.create_user(username='obama', password='nopassword')  # 새로운 포트스 생성을 위해 user를 생성해줌.

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        # 미분류(1)이 있어야 함
        self.assertIn('미분류 (1)', category_card.text)
        # 정치/사회(1)이 있어야 함
        self.assertIn('정치/사회 (1)', category_card.text)



    def test_post_list_no_post(self):  # 함수 이름에 'test_'는 약속(필수)임 -> 오류 가능성도 있음
        response = self.client.get('/blog/')  # 클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함

        title = soup.title  # 이렇게 하면 해당 소스의 title을 바로 가져올 수 있다.

        # print(title)    # -> 태그 포함 출력
        # print(title.text)   # 사람이 보는 것과 같이 태그 제외하고 출력

        self.assertIn(title.text, 'Blog')  # 타이틀이 Blog인지 테스트

        self.check_navbar(soup)
        # navbar = soup.find('div', id='navbar')        함수로 구현 안했을 경우
        # self.assertIn('Blog', navbar.text)
        # self.assertIn('About me', navbar.text)

        self.assertEqual(Post.objects.count(),
                         0)  # db 명령 (get, all 과 같은 것) -> 테스트 코드 내에서 아직 포스트를 생성하지 않았기때문에 포스트의 개수는 0이다.
        self.assertIn('아직 게시물이 없습니다.', soup.body.text)  # 포스트 0개이기 때문에 html 내에서 아직 게시물이 없습니다. 가 동작하고, 따라서 테스트도 통과한다.

    def test_post_list_with_post(self):
        tag_america = create_tag(name='america')
        # 포스트 생성! -> 테스트는 db를 제로베이스에서 실행하기 때문에 브라우저 상황과는 관계 없이 새로 생성해야함.
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )

        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title="The Second post",
            content="Hello World. We are the world.",
            author=self.author_000,
            category=create_category(name='정치/사회')
        )

        post_001.tags.add(tag_america)
        post_001.save()

        self.assertGreater(Post.objects.count(), 0)  # 0개보다 많으면 통과

        response = self.client.get('/blog/')  # 클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명
        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다.', body.text)  # 게시물이 하나 있기 때문에 이게 출력 안됨,, 따라서 테스트 통과함(notin!!)
        self.assertIn(post_000.title, body.text)

        post_000_read_more_btn = body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_btn['href'],
                         post_000.get_absolute_url())  # 버튼을 눌렀을 때의 링크가 해당 포스트의 url과 일치하는지 검사

        # category card에서
        self.check_right_side(soup)

        # main_div에서 정치/시회가 있어야 함
        main_div = soup.find('div', id='main-div')
        self.assertIn('정치/사회', main_div.text)
        # 미분류 있어야함
        self.assertIn('미분류', main_div.text)

        # Tag
        post_card_000 = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#america', post_card_000.text)   #tag가 해당 post의 card마다 있다.

    # 페이지네이션
    def test_pagination(self):
        # post가 적은 경우
        for i in range(0, 3):
            post_000 = create_post(
                title="The post No. {}".format(i),
                content="{}".format(i),
                author=self.author_000,
            )

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명
        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함

        self.assertNotIn('Older', soup.body.text)
        self.assertNotIn('Newer', soup.body.text)

        # post가 많은 경우
        for i in range(3, 10):
            post_000 = create_post(
                title="The post No. {}".format(i),
                content="{}".format(i),
                author=self.author_000,
            )

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명
        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함

        self.assertIn('Older', soup.body.text)
        self.assertIn('Newer', soup.body.text)

    # 함수가 실행하는 순간에는, 포스트가 하나도 없음
    def test_post_detail(self):
        # self.assertGreater(Post.objects.count(), 0)  # 0개보다 많으면 통과     -> 함수 동작시에는 다시 포스트가 0개.. 따라서 에러가 나옴!!(테스트 통과 x)
        # 포스트 생성! -> 테스트는 db를 제로베이스에서 실행 q하기 때문에 브라우저 상황과는 관계 없이 새로 생성해야함.

        category_politics = create_category(name='정치/사회')
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
            category=category_politics
        )
        comment_000 = create_comment(post_000, text='a test comment', author=self.user_obama)
        comment_001 = create_comment(post_000, text='a test comment', author=self.author_000)

        tag_america = create_tag(name='america')
        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title="The Second post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)  # 0개보다 많으면 통과
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url,
                         '/blog/{}/'.format(post_000.pk))  # post_000.get_absolute_url()의 결과가 뒤의 인자와 같은지 평가하는 함수

        response = self.client.get(post_000_url)  # 클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        title = soup.title  # 이렇게 하면 해당 소스의 title을 바로 가져올 수 있다.

        # print(title)    # -> 태그 포함 출력
        # print(title.text)   # 사람이 보는 것과 같이 태그 제외하고 출력
        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))
        # 각 포스터 내에 네비게이션바가 있는지 확인하는 테스트
        self.check_navbar(
            soup)  # 원래는 post_detail.html 내에 네비바가 없으므로 에러!! -> html 수정 후 (네비 바 추가) 테스트 돌려보기! 이것이 tdd 개발 방식!!

        body = soup.body
        main_div = body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)

        self.assertIn(post_000.content, main_div.text)
        # category card에서
        self.check_right_side(soup)

        # comment
        comment_div = main_div.find('div', id='comment-list')
        self.assertIn(comment_000.author.username, comment_div.text)
        self.assertIn(comment_000.text, comment_div.text)

        # Tag
        self.assertIn('america', main_div.text)  # tag가 해당 post의 card마다 있다.

        self.assertIn(category_politics.name, main_div.text)# 카테고리가 main_div에 있다.
        self.assertNotIn('EDIT', main_div.text)# edit 버튼이 로그인 하지 않은 경우 보이지 않는다.

        login_success = self.client.login(username='smith', password='nopassword')  # 로그인을 한 경우에는
        self.assertTrue(login_success)
        # 로그인을 위해 페이지 새로고침을 하는 것과 같은 개념!!
        response = self.client.get(post_000_url)  # 클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함

        main_div=soup.find('div', id='main-div')
        self.assertEqual(post_000.author, self.author_000)# post.author와 login한 사용자가 동일하면
        self.assertIn('EDIT', main_div.text)# edit 버튼이 있다.

        # 그렇지 않은 경우에는 없다.
        login_success = self.client.login(username='obama', password='nopassword')  # 로그인을 한 경우에는
        self.assertTrue(login_success)
        # 로그인을 위해 페이지 새로고침을 하는 것과 같은 개념!!
        response = self.client.get(post_000_url)  # 클라이언트가 해당 브라우저에 접속해서 무엇을 가져올 것임
        self.assertEqual(response.status_code, 200)  # 가져온 것이 200이면 문제가 x ->404에러가 x를 증명

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함

        main_div = soup.find('div', id='main-div')
        self.assertEqual(post_000.author, self.author_000)  # post.author와 login한 사용자가 동일하면
        self.assertNotIn('EDIT', main_div.text)  # edit 버튼이 있다.

        comments_div = main_div.find('div', id='comment-list')
        comment_000_div = comments_div.find('div', id='comment-id-{}'.format(comment_000.pk))
        self.assertIn('edit', comment_000_div.text)
        self.assertIn('delete', comment_000_div.text)

        comment_001_div = comments_div.find('div', id='comment-id-{}'.format(comment_001.pk))
        self.assertNotIn('edit', comment_001_div.text)
        self.assertNotIn('delete', comment_001_div.text)

    def test_post_list_by_category(self):
        category_politics = create_category(name='정치/사회')

        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )
        post_001 = create_post(
            title="The Second post",
            content="Hello World. We are the world.",
            author=self.author_000,
            category=category_politics
        )

        response = self.client.get(category_politics.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        # self.assertEqual('Blog - {}'.format(category_politics.name), soup.title.text)

        main_div = soup.find('div', id = 'main-div')
        self.assertNotIn('미분류', main_div.text)
        self.assertIn(category_politics.name, main_div.text)

        def test_post_list_by_category(self):
            category_politics = create_category(name='정치/사회')

            post_000 = create_post(
                title="The first post",
                content="Hello World. We are the world.",
                author=self.author_000,
            )
            post_001 = create_post(
                title="The Second post",
                content="Hello World. We are the world.",
                author=self.author_000,
                category=category_politics
            )

            response = self.client.get(category_politics.get_absolute_url())
            self.assertEqual(response.status_code, 200)

            soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
            # self.assertEqual('Blog - {}'.format(category_politics.name), soup.title.text)

            main_div = soup.find('div', id='main-div')
            self.assertNotIn('미분류', main_div.text)
            self.assertIn(category_politics.name, main_div.text)


        # 미분류 눌렀을 때 미분류 잘 모아주는지 확인 테스트
    def test_post_list_no_category(self):
        category_politics = create_category(name='정치/사회')

        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )
        post_001 = create_post(
            title="The Second post",
            content="Hello World. We are the world.",
            author=self.author_000,
            category=category_politics
        )

        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        # self.assertEqual('Blog - {}'.format(category_politics.name), soup.title.text)

        main_div = soup.find('div', id='main-div')
        self.assertIn('미분류', main_div.text)
        self.assertNotIn(category_politics.name, main_div.text)

    def test_tag_page(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title="Stay Fool",
            content="Story about Jobs",
            author=self.author_000,
        )
        post_001.tags.add(tag_001)
        post_001.save()

        response = self.client.get(tag_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함

        main_div = soup.find('div', id='main-div')
        blog_h1 = main_div.find('h1', id='blog-list-title')

        self.assertIn('#{}'.format(tag_000.name), blog_h1.text)
        self.assertIn(post_000.title, main_div.text)
        self.assertNotIn(post_001.title, main_div.text)

    def test_post_create(self):
        response = self.client.get('/blog/create/')
        self.assertNotEqual(response.status_code, 200)

        # 로그인 해야지만 /create 사이트 접속 가능해야함
        self.client.login(username='smith', password='nopassword')
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        main_div = soup.find('div', id='main-div')


    def test_post_update(self):
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )

        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')

        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        main_div = soup.find('div', id='main-div')

        self.assertNotIn('Created', main_div.text)
        self.assertNotIn('Author', main_div.text)

    def test_new_comment(self):
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )

        login_success = self.client.login(username='smith', password='nopassword')  # 로그인을 한 경우에는
        self.assertTrue(login_success)

        # redirect로 온 것이기 때문에, follow라는 것을 해줘야한다.
        response = self.client.post(
            post_000.get_absolute_url() + 'new_comment/',
            {'text' : 'A test comment for the first post'},
            follow = True
        )  # post 방식으로 서버에 무언가 전달할 때
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn('A test comment', main_div.text)

    def test_delete_comment(self):
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )

        comment_000 = create_comment(post_000, text='a test comment', author=self.user_obama)
        comment_001 = create_comment(post_000, text='a test comment', author=self.author_000)

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)

# 로그인 사용자만, 본인의 댓글을 지울 수 있도록!
        # (로그인을 다른 사람으로 했을 때)
        login_success = self.client.login(username = 'smith', password = 'nopassword')
        self.assertTrue(login_success)
# delete comment를 class뷰로 구현하면서, 예외를 발생시켰기 때문에 with 구문을 추가해줘야한다.
        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow=True)
        # 원래는 with 구문 없이 이 상태였음.

        # response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow=True)
            self.assertEqual(Comment.objects.count(), 2)
            self.assertEqual(post_000.comment_set.count(), 2)

#로그인을 오바마로 했을 때
        login_success = self.client.login(username='obama', password='nopassword')
        response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow = True)
        self.assertEqual(response.status_code, 200)


        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(post_000.comment_set.count(), 1)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        main_div = soup.find('div', id='main-div')

        self.assertNotIn('obama', main_div)

    def test_edit_comment(self):
        post_000 = create_post(
            title="The first post",
            content="Hello World. We are the world.",
            author=self.author_000,
        )

        comment_000 = create_comment(post_000, text='I am president of the US', author=self.user_obama)
        comment_001 = create_comment(post_000, text='a test comment', author=self.author_000)

        # SMITH로 로그인한 경우
        login_success = self.client.login(username='smith', password = 'nopassword')
        self.assertTrue(login_success)
        # 로그인을 하지 않았을 때
        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))

        # 댓글의 저자로 로그인한 경우(지금으로서는, 오바마로 로그인) 에러 나면 안됨
        login_success = self.client.login(username='obama', password='nopassword')
        self.assertTrue(login_success)

        response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        self.assertIn('Edit Comment: ', soup.body.h3.text)

        response = self.client.post(
            '/blog/edit_comment/{}/'.format(comment_000.pk),
            {'text': 'I was president of the US'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')  # 컨텐츠(내용)를 가져와서 html 파서로 파싱을 함
        self.assertNotIn('I am president of the US', soup.body.text)
        self.assertIn('I was president of the US', soup.body.text)
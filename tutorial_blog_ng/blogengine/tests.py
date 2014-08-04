from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from blogengine.models import Post
import markdown
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

class BaseAcceptanceTest(LiveServerTestCase):
    def setUp(self):
        self.client = Client()

class PostTest(TestCase):
    def test_create_post(self):
        #create the auther
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        #create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        #create the Post
        post = Post()

        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site

        post.save()

        #check we can find import
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1 )
        only_post = all_posts[0]
        self.assertEquals(only_post, post)


        # Check attributes
        self.assertEquals(only_post.title,'My first post')
        self.assertEquals(only_post.text, 'This is my first blog post')
        self.assertEquals(only_post.slug, 'my-first-post')
        self.assertEquals(only_post.site.name, 'example.com')
        self.assertEquals(only_post.site.domain, 'example.com')
        self.assertEquals(only_post.pub_date.day, post.pub_date.day)
        self.assertEquals(only_post.pub_date.month, post.pub_date.month)
        self.assertEquals(only_post.pub_date.year, post.pub_date.year)
        self.assertEquals(only_post.pub_date.hour, post.pub_date.hour)
        self.assertEquals(only_post.pub_date.minute, post.pub_date.minute)
        self.assertEquals(only_post.pub_date.second, post.pub_date.second)
        self.assertEquals(only_post.author.username, 'testuser')
        self.assertEquals(only_post.author.email, 'user@example.com')

class AdminTest(BaseAcceptanceTest):
    fixtures = ['users.json']

    def test_login(self):
        #Get login page
        response = self.client.get('/admin/')

        #check response code
        self.assertEquals(response.status_code, 200)

        #check 'log in' in response
        self.assertTrue('Log in' in response.content)

        #log the user in
        self.client.login(username='bobsmith', password="password")

        #chheck response code
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)

        #check 'log out' in response
        self.assertTrue('Log out' in response.content)

    def test_logout(self):
        #log the user in
        self.client.login(username='bobsmith', password="password")

        #chheck response code
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)

        #check 'log out' in response
        self.assertTrue('Log out' in response.content)

        #log out
        self.client.logout()

        #check response code
        response = self.client.get('/admin/')
        self.assertEquals(response.status_code, 200)

        #check 'Log in' in response
        self.assertTrue('Log in' in response.content)

    def test_create_post(self):
        #login
        self.client.login(username='bobsmith', password="password")

        #check response code
        response = self.client.get('/admin/blogengine/post/add/')
        self.assertEquals(response.status_code, 200)

        # Create the new post
        response = self.client.post('/admin/blogengine/post/add/', {
            'title': 'My first post',
            'text': 'This is my first post',
            'pub_date_0': '2013-12-28',
            'pub_date_1': '22:00:04',
            'slug': 'my-first-post',
            'site': '1'
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new post now in database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

    def test_edit_post(self):
        #create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        #create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Edit the post
        response = self.client.post('/admin/blogengine/post/1/', {
            'title': 'My second post',
            'text': 'This is my second blog post',
            'pub_date_0': '2013-12-28',
            'pub_date_1': '22:00:04',
            'slug': 'my-second-post',
            'site':'1'
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check changed successfully
        self.assertTrue('changed successfully' in response.content)

        # Check post amended
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post.title, 'My second post')
        self.assertEquals(only_post.text, 'This is my second blog post')

    def test_delete_post(self):
        #create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        #create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.site = site
        post.author = author
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Delete the post
        response = self.client.post('/admin/blogengine/post/1/delete/', {
            'post': 'yes'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check deleted successfully
        self.assertTrue('deleted successfully' in response.content)

        # Check post amended
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 0)

class PostViewTest(BaseAcceptanceTest):
    def test_index(self):
        #create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        #create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        #create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.site = site
        post.author = author
        post.save()

        #check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

        #fetch the test_index
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

        #check the post title is in the response
        self.assertTrue(post.title in response.content)

        #check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        #check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)
        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_post_page(self):
        #create the author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()
        
        #create the site
        site = Site()
        site.name = 'example.com'
        site.domain = 'example.com'
        site.save()

        #create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.site = site
        post.author = author
        post.save()

        #check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        #get post url
        post_url = only_post.get_absolute_url()

        #fetch the post
        response = self.client.get(post_url)
        self.assertEquals(response.status_code, 200)

        #check the post title is in the response
        self.assertTrue(post.title in response.content)

        #check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        #check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)       

class FlatPageViewTest(BaseAcceptanceTest):
    def test_create_flag_page(self):
        #create flat page
        page = FlatPage()
        page.url = '/about/'
        page.title ='About me'
        page.content = 'All about me'
        page.save()

        #add the site
        page.sites.add(Site.objects.all()[0])
        page.save()

        #check new page saved
        all_pages = FlatPage.objects.all()
        self.assertEquals(len(all_pages), 1)
        only_page = all_pages[0]
        self.assertEquals(only_page,page)

        #check data correct
        self.assertEquals(only_page.url, '/about/')
        self.assertEquals(only_page.title, 'About me')
        self.assertEquals(only_page.content, 'All about me')

        #get url
        page_url = only_page.get_absolute_url()

        #get the page
        response = self.client.get(page_url)
        self.assertEquals(response.status_code, 200)

        #check title and content in response
        self.assertTrue('About me' in response.content)
        self.assertTrue('All about me' in response.content)


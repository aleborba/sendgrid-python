import os
import unittest2 as unittest
import json
import sys
from sendgrid import SendGridClient, Mail

class TestSendGrid(unittest.TestCase):
    def setUp(self):
        self.sg = SendGridClient(os.getenv('SG_USER'), os.getenv('SG_PWD'))

    @unittest.skipUnless(sys.version_info < (3, 0), 'only for python2')
    def test_unicode_recipients(self):
        recipients = [unicode('test@test.com'), unicode('guy@man.com')]
        m = Mail(to=recipients,
                 subject='testing',
                 html='awesome',
                 from_email='from@test.com')

        mock = {'to[]': ['test@test.com', 'guy@man.com']}
        result = self.sg._build_body(m)

        self.assertEqual(result['to[]'], mock['to[]'])

    def test_send(self):
        m = Mail()
        m.add_to('John, Doe <john@email.com>')
        m.set_subject('test')
        m.set_html('WIN')
        m.set_text('WIN')
        m.set_from('doe@email.com')
        m.add_substitution('subKey', 'subValue')
        m.add_section('testSection', 'sectionValue')
        m.add_category('testCategory')
        m.add_unique_arg('testUnique', 'uniqueValue')
        m.add_filter('testFilter', 'filter', 'filterValue')
        m.add_attachment_stream('testFile', 'fileValue')
        url = self.sg._build_body(m)
        url.pop('api_key', None)
        url.pop('api_user', None)
        url.pop('date', None)
        test_url = json.loads('''
            {
                "to[]": ["john@email.com"],
                "toname[]": ["John Doe"],
                "html": "WIN",
                "text": "WIN",
                "subject": "test",
                "files[testFile]": "fileValue",
                "from": "doe@email.com"
            }
            ''')
        test_url['x-smtpapi'] = json.dumps(json.loads('''
            {
                "to" : ["John, Doe <john@email.com>"],
                "sub": {
                    "subKey": ["subValue"]
                },
                "section": {
                    "testSection":"sectionValue"
                },
                "category": ["testCategory"],
                "unique_args": {
                    "testUnique":"uniqueValue"
                },
                "filters": {
                    "testFilter": {
                        "settings": {
                            "filter": "filterValue"
                        }
                    }
                }
            }
            '''))
        self.assertEqual(url, test_url)

    @unittest.skipUnless(sys.version_info < (3, 0), 'only for python2')
    def test__build_body_unicode(self):
        """test _build_body() handles encoded unicode outside ascii range"""
        from_email = '\xd0\x9d\xd0\xb8\xd0\xba\xd0\xb0@email.com'
        from_name = '\xd0\x9a\xd0\xbb\xd0\xb0\xd0\xb2\xd0\xb4\xd0\xb8\xd1\x8f'
        subject = '\xd0\x9d\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xb6\xd0\xb4\xd0\xb0'
        text = '\xd0\x9d\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xb6\xd0\xb4\xd0\xb0'
        html = '\xd0\x9d\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xb6\xd0\xb4\xd0\xb0'
        reply_to = '\xd0\x9d\xd0\xb8\xd0\xba\xd0\xb0@email.com'
        m = Mail()
        m.add_to('John, Doe <john@email.com>')
        m.set_subject(subject)
        m.set_html(html)
        m.set_text(text)
        m.set_from("%s <%s>" % (from_name, from_email))
        url = self.sg._build_body(m)
        self.assertEqual(from_email, url['from'])
        self.assertEqual(from_name, url['fromname'])
        self.assertEqual(subject, url['subject'])
        self.assertEqual(text, url['text'])
        self.assertEqual(html, url['html'])


if __name__ == '__main__':
    unittest.main()

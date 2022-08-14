import praw, os, datetime, traceback
from dotenv import load_dotenv
from functools import wraps

load_dotenv()


def combomethod(func):
    @wraps(func)
    def wrap_template(self, *args, **kwargs):
        return func(self, self.__class__, *args, **kwargs)

    return wrap_template


class RedditReplyBot:
    REPLY_DICT = {}  # bu arkadaşın girişlerinin tek kelime olması lazım
    MAX_WORDS = None
    DOWNVOTE_THRESHOLD = -5
    SUBREDDIT = ""
    DEBUG = False
    DOWNVOTE_CHECK_INTERVAL = 10
    DOWNVOTE_CHECK_LIMIT = 100
    REPLY = True

    def __init__(self, c_id, c_sec, u_a, username, password) -> None:
        self.cls = self.__class__
        self.reddit = praw.Reddit(
            client_id=c_id,
            client_secret=c_sec,
            user_agent=u_a,
            username=username,
            password=password,
        )
        if self.cls.DEBUG:
            print(f"logged in as u/{self.reddit.user.me()}")

    @combomethod
    def run(self, cls):
        sub = self.reddit.subreddit(cls.SUBREDDIT)
        comment_stream = sub.stream.comments(skip_existing=True, pause_after=-1)
        submission_stream = sub.stream.submissions(skip_existing=True, pause_after=-1)
        i = 0
        while True:
            try:
                for comment in comment_stream:
                    if comment is None:
                        break
                    if cls.DEBUG:
                        print(f'got comment "{comment.body}" by u/{comment.author}')
                    self.handle(comment=comment)

                for submission in submission_stream:
                    if submission is None:
                        break
                    if cls.DEBUG:
                        print(
                            f'got post {submission.title}:"{submission.selftext}" by u/{submission.author}'
                        )
                    self.handle(post=submission)
                if i // cls.DOWNVOTE_CHECK_INTERVAL != 0:
                    i = 0
                    for comment in self.reddit.user.me().comments.new(
                        limit=cls.DOWNVOTE_CHECK_LIMIT
                    ):
                        if cls.DEBUG:
                            print(f"this is a comment from me: {comment.body}")
                        if comment.score < -10:
                            comment.delete()
                else:
                    i += 1
            except Exception as e:
                with open("error.log", "a") as f:
                    f.write(
                        f"""{datetime.datetime.utcnow()}: caught an exception: {str(e)}:\n{traceback.format_exc()}\n"""
                    )

    @combomethod
    def handle(self, cls, comment: praw.models.Comment = None, post: praw.models.Submission = None):
        if comment is not None:  # comment gelmiş
            data = ("", comment.body)
            author = comment.author
            obj = comment
        elif post is not None:  # post gelmiş
            data = (post.title, post.selftext)
            author = post.author
            obj = post

        if author.name == self.reddit.user.me().name:
            return

        length = [len(i.split()) for i in data]
        if length[0] > cls.MAX_WORDS or length[1] > cls.MAX_WORDS:
            return

        text = f"{data[0]} {data[1]}" if data[0] != "" else data[1]

        reply = [i[1] for i in cls.REPLY_DICT.items() if i[0] in text.split()]

        if len(reply) == 1:
            if cls.REPLY:
                obj.reply(body=reply[0])
            print(f'replied to u/{author}\'s text "{text}" with "{reply[0]}"')


class ima_ninana(RedditReplyBot):
    REPLY_DICT = {
        "nereyi": "ananın amını",
        "nereye": "ananın amına",
        "nereden": "ananın amından",
        "nerede": "ananın amında",
        "neyi": "ananın amını",
        "neden": "ananın amından dolayı",
    }
    SUBREDDIT = "kgbtr+u_insanolanbiri+u_ima_ninana"
    MAX_WORDS = 10
    DOWNVOTE_THRESHOLD = 10
    DEBUG = False
    DOWNVOTE_CHECK_INTERVAL = 100
    DOWNVOTE_CHECK_LIMIT = 1000
    REPLY = True

def main():
    bot = ima_ninana(
        c_id=os.getenv("BOT_CLIENT_ID"),
        c_sec=os.getenv("BOT_CLIENT_SECRET"),
        u_a=os.getenv("BOT_USER_AGENT"),
        username=os.getenv("BOT_USERNAME"),
        password=os.getenv("BOT_PASSWORD"),
    )


    bot.run()

if __name__ == "__main__":
    main()
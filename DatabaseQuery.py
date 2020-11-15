import boto3,time
from boto3.dynamodb.conditions import Key, Attr
import filecmp
import emails
from botocore.config import Config

session = boto3.Session(
    region_name="eu-west-2",
    aws_access_key_id="AKIAIKW6OHS2HYDAQ5PQ",
    aws_secret_access_key="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",
)

client = session.resource("dynamodb")
occs = dict()

def findSeatNow(room):
        bookings= client.Table("Bookings")
        response = bookings.scan(
        FilterExpression=
            Key('seat').eq(room) & Key('end').gt(int(time.time())) & Key('start').lt(int(time.time()))
        )
        if len(response["Items"]) > 0:
            items = response['Items'][0]["ID"]
            print(items)
            users = client.Table("Users")
            user_q = users.scan(FilterExpression=Key('Username').eq("bzrr62"))
            phone = user_q['Items'][0]["phone"]
            print(phone)
        return items, phone

#findSeatNow()



while True:
    if filecmp.cmp("trig1.txt","trig2.txt") == False:
        file = open(r"trig2.txt","r+")
        room = file.readline()
        name, phone = findSeatNow(room)
        file.seek(0)
        file.truncate()
        if room not in occs:
            occs[room] = 1
            client2 = boto3.client(
                "sns",
                aws_access_key_id="AKIAQSISZZFTFXP7T5EP",
                aws_secret_access_key="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",
                region_name="eu-west-2"
            )

            client2.publish(
                PhoneNumber=phone,
                Message="Please wear your mask! \n\n- Everyone"
            )
        elif occs[room] >= 1:
            # Prepare the email
            message = emails.html(
                html="<h1>Come to zoom</h1><strong>I've got something to tell you!</strong>",
                subject="Join Zoom",
                mail_from="bzrr62@durham.ac.uk",
            )
            message.attach(data=open('drone.png', 'rb'), filename='drone.png')
            # Send the email
            r = message.send(
                to= name + "@durham.ac.uk",
                smtp={
                    "host": "email-smtp.eu-west-2.amazonaws.com",
                    "port": 587,
                    "timeout": 5,
                    "user": "AKIAQSISZZFTL6EIHPHL",
                    "password": "BB9H3NCJkH4YyCpEEmudNmAQha6jsjV58dhfgTfNw7e3",
                    "tls": True,
                },
            )

            # Check if the email was properly sent
            assert r.status_code == 250


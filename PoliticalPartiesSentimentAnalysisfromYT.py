import re
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
import nltk
from googleapiclient.errors import HttpError

# Download necessary nltk resources
nltk.download('punkt')

# Replace with your YouTube Data API key
API_KEY = 'AIzaSyCJ8vS6pQwChsMQZjAYBmVztRANFPutOPY'


# Function to clean YouTube comments
def clean_comment(comment):
    # Remove URLs, special characters, etc.
    return re.sub(r"http\S+|www\S+|https\S+|[^a-zA-Z\s]", '', comment, flags=re.MULTILINE).strip()


# Function to perform sentiment analysis on the cleaned comment
def analyze_sentiment(comment):
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


# Function to fetch YouTube video comments related to the political party
def get_youtube_comments(query, max_comments=100):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Search for videos related to the political party
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=10
    ).execute()

    # Collect video IDs
    video_ids = [item['id']['videoId'] for item in search_response['items'] if 'videoId' in item['id']]

    comments = []
    for video_id in video_ids:
        try:
            # Fetch comments from the video
            comment_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_comments,
                textFormat="plainText"
            ).execute()

            for item in comment_response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(clean_comment(comment))
        except HttpError as e:
            error = e.content.decode("utf-8")
            if 'commentsDisabled' in error:
                print(f"Comments are disabled for video ID {video_id}, skipping...")
            else:
                raise

    return comments


# Function to calculate the sentiments of the comments
def get_sentiments_for_party(party_name, max_comments=100):
    comments = get_youtube_comments(party_name, max_comments)

    sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
    for comment in comments:
        sentiment = analyze_sentiment(comment)
        sentiments[sentiment] += 1

    return sentiments


# Function to plot the sentiment analysis results
def plot_sentiments(sentiments, party_name):
    labels = sentiments.keys()
    sizes = sentiments.values()
    colors = ['green', 'blue', 'red']
    explode = (0.1, 0, 0)  # explode the 1st slice for visibility

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f"Sentiment Analysis for {party_name}")
    plt.show()


# Main function for user input and running the sentiment analysis
def main():
    party_name = input("Enter the name of the political party: ")
    sentiment_data = get_sentiments_for_party(party_name)
    print(f"Sentiment Analysis for {party_name}: {sentiment_data}")
    plot_sentiments(sentiment_data, party_name)


if __name__ == "__main__":
    main()

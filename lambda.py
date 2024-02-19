import json
import boto3

Questions_to_be_asked = ["Q 01. What is your name?","Q 02. What is your address?", "Q o3. What is your phone number?"]

def lambda_handler(event, context):
    # TODO implement

    ### Extracting transcript from the json file
    s3_client = boto3.client('s3')
    #  Get the S3 bucket and object details from the event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']

    # Retrieve the transcribed text file from S3
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    text_content = response['Body'].read().decode('utf-8')
    text_content_json = json.loads(text_content)
    call_conversation = text_content_json["results"]["transcripts"][0]["transcript"]
    print("Able to read data from json: ", call_conversation)
 
    ### Formatting/Preparing data/transcript to extract best result from bedrock
    # call_conversation = """Hi Prasanta!. Hi who is this? I am calling you from Pacific Life. Okay. This call is regarding your recent policy claim. Hmm Is this good time to talk you? Yes please go ahead. So, tell me your full name please. My name is Prasanta Paul. Right next, What is your address? My address is 1234 Main St, Anytown, USA. Right next, What is your phone number? My phone number is 000000000000. Thank you very much."""

    prompt = f"Suppose I am from a car insurance provider company. My task is to call the policyholder to do some investigation by asking relevent questions like {Questions_to_be_asked}. Now your task is to answer these questions and provide the answer of all the questions in json format. If you don't find relevent answer this put null. Call conversation between policyholder and investigator: {call_conversation}"

    ### Making API call on Bedrock runtime to extract answer from the transcript
    bedrock_rtime = boto3.client (service_name="bedrock-runtime", region_name= "us-east-1")       
    kwargs = {"modelId": "ai21.j2-ultra-v1", "contentType": "application/json", "accept": "*/*",
        "body": "{\"prompt\":\""+ prompt +"\",\"maxTokens\":200,\"temperature\":0.7,\"topP\":1,\"stopSequences\":[],\"countPenalty\":{\"scale\":0},\"presencePenalty\":{\"scale\":0},\"frequencyPenalty\":{\"scale\":0}}"}
    response = bedrock_rtime.invoke_model(**kwargs)
    response_body = json.loads(response.get('body').read())
    extrected_q_and_a  = response_body.get('completions')[0].get('data').get('text')
    print("Able to extrected_q_and_a: ", extrected_q_and_a)

    # Saving this extracted answer in the same S3 bucket as the transcript in folder:"03-extracted-data/"
    s3_client.put_object(Body=extrected_q_and_a, Bucket=s3_bucket, Key="03-extracted-data/" + s3_key.split("/")[-1])
    print("Able to save extracted answer in S3 bucket: ", s3_bucket)
    return {'statusCode': 200, 'body': extrected_q_and_a}
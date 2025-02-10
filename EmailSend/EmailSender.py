import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import asyncio
import aiosmtplib
load_dotenv()

# Sender's email credentials and SMTP settings
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

async def send_email(smtp, recipient_email, recipient_name, id_card_link, retry_count=3):
    for attempt in range(retry_count):
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Bcc'] = SENDER_EMAIL
            msg['Subject'] = "Important: BCA Roadmap 2.0 Event Details and ID Card Access"
            
            # HTML message with proper formatting
            html_message = f"""\
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Dear {recipient_name},</p>
    
    <p>We are excited to have you join us for the BCA Roadmap 2.0 event.</p>

    <h3 style="color: #2c5282;">Event Details:</h3>
    <ul>
        <li><strong>Date:</strong> 2081 Falgun 02</li>
        <li><strong>Venue:</strong> Mechi Multiple Campus, Humanities Building Seminar Hall</li>
    </ul>

    <h3 style="color: #2c5282;">Your ID Card:</h3>
    <p>You can download your ID card using the following link:<br>
    <a href="{id_card_link}" style="color: #3182ce;">{id_card_link}</a></p>

    <p><em>Please take a screenshot of your ID card and present it at the event.</em></p>

    <p>If you notice any discrepancies or have any questions, please contact your class representative 
    or email us at <a href="mailto:mechimavericks@gmail.com" style="color: #3182ce;">mechimavericks@gmail.com</a>.</p>

    <p>Best regards,<br>
    Mechi Mavericks/BCA Association</p>
  </body>
</html>
"""
            # Only attach HTML version
            msg.attach(MIMEText(html_message, 'html'))
            
            await smtp.send_message(msg)
            print(f"✓ Email sent to {recipient_email} successfully!")
            return True
            
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"Attempt {attempt + 1} failed for {recipient_email}: {str(e)}")
                await asyncio.sleep(2)  # Wait before retry
            else:
                print(f"❌ Failed to send email to {recipient_email} after {retry_count} attempts: {str(e)}")
                return False

async def send_emails_concurrently(contacts):
    # Gmail limits: 500 per day, max 100 recipients per message
    BATCH_SIZE = 10  # Process 10 emails at a time
    BATCH_DELAY = 30  # 30 seconds between batches
    
    smtp = aiosmtplib.SMTP(
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        use_tls=False,
        start_tls=True
    )
    
    try:
        await smtp.connect()
        await smtp.login(SENDER_EMAIL, APP_PASSWORD)
        
        total_sent = 0
        failed_sends = []
        
        # Debug print to see total contacts
        print(f"Total contacts to process: {len(contacts)}")
        
        # Process emails in batches
        for start_idx in range(0, len(contacts), BATCH_SIZE):
            batch = contacts.iloc[start_idx:start_idx + BATCH_SIZE]
            tasks = []
            
            print(f"\nProcessing batch {start_idx//BATCH_SIZE + 1} of {(len(contacts) + BATCH_SIZE - 1)//BATCH_SIZE}...")
            print(f"Batch size: {len(batch)} emails")
            
            for _, row in batch.iterrows():
                recipient_email = row['email']
                recipient_name = row['fullname']
                recipient_id = row['_id']
                id_card_link = f"https://idcard.mechimavericks.tech/?id={recipient_id}"
                
                print(f"Queuing email for {recipient_name} ({recipient_email})")
                task = asyncio.create_task(
                    send_email(smtp, recipient_email, recipient_name, id_card_link)
                )
                tasks.append(task)
            
            # Wait for current batch to complete
            results = await asyncio.gather(*tasks)
            total_sent += sum(1 for r in results if r)
            failed_sends.extend([
                email for email, success in zip(batch['email'], results) if not success
            ])
            
            if start_idx + BATCH_SIZE < len(contacts):
                print(f"Waiting {BATCH_DELAY} seconds before next batch...")
                await asyncio.sleep(BATCH_DELAY)
                
        print(f"\nEmail sending complete!")
        print(f"Successfully sent: {total_sent}/{len(contacts)}")
        if failed_sends:
            print(f"Failed to send to {len(failed_sends)} recipients:")
            for email in failed_sends:
                print(f"- {email}")
                
    finally:
        await smtp.quit()

if __name__ == "__main__":
    contacts_file = "studentdata.csv"
    contacts = pd.read_csv(contacts_file)
    print(contacts)
    asyncio.run(send_emails_concurrently(contacts))
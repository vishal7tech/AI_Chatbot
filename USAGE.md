# AI Chatbot Part 3 - Usage Guide

## 🎯 Step-by-Step Usage Guide

### For Beginners - Complete Walkthrough

## 1. Starting the Application

### Step 1: Open Command Prompt
```bash
# Navigate to project folder
cd "c:\Users\ACER\OneDrive\Desktop\Project\rule_based_chatbot"

# Activate virtual environment
venv\Scripts\activate

# Start the application
python app.py
```

### Step 2: Open Browser
Visit: http://localhost:5000

You should see: **"Chat with AI Assistant 🤖"**

## 2. Training the AI Model (First Time Only)

### Option A: Using Admin Panel (Easiest)
1. Go to: http://localhost:5000/admin
2. Look for orange button: **"🧠 Train AI Model"**
3. Click the button
4. Wait for "AI Model Training Started!" message
5. Wait 2-3 minutes for training to complete
6. You'll see a success message when done

### Option B: Using Jupyter Notebook (Advanced)
1. Open command prompt in project folder
2. Run: `jupyter notebook train_intent_model.ipynb`
3. Run all cells (Cell → Run All)
4. Wait for training to complete
5. Close the notebook when done

## 3. Using the Chat Interface

### Basic Chatting
1. Type in the input box: "hello"
2. Press Enter or click Send
3. See the AI response with confidence score
4. Try different messages

### Understanding Confidence Scores
- 🎯 **Green (80%+)**: High confidence - AI is very sure
- 🤔 **Yellow (60-79%)**: Medium confidence - AI is somewhat sure  
- ⚠️ **Red (<60%)**: Low confidence - AI is guessing

### Sample Conversations to Try

#### Greeting Conversation:
```
You: hi
AI: Hello! How can I help you today? 🎯 High Confidence: 95.2%

You: kya haal hai
AI: Hi there! Welcome! 🎯 High Confidence: 91.8%

You: thanks
AI: You're welcome! 🎯 High Confidence: 87.5%
```

#### Fees Inquiry:
```
You: fees kitne hain?
AI: Our course fee is ₹5000 for 3 months. 🤔 Medium Confidence: 75.3%

You: course price
AI: Fees structure: Basic - ₹3000, Advanced - ₹5000. 🎯 High Confidence: 82.1%
```

#### Appointment Booking:
```
You: appointment book karna hai
AI: You can book appointment by calling 9876543210. 🤔 Medium Confidence: 68.9%

You: meeting chahiye
AI: Visit our office between 10AM-6PM for appointment. 🎯 High Confidence: 79.2%
```

## 4. Managing Intents and Data (Admin Functions)

### Adding New Intent Categories

#### Step 1: Go to Admin Panel
Visit: http://localhost:5000/admin

#### Step 2: Add New Intent
1. Find "Add New Intent" section
2. **Tag**: Enter category name (e.g., "weather")
3. **Response**: Enter a default response (e.g., "It's sunny today!")
4. Click **"Add Intent"**

#### Step 3: Add Training Patterns
1. Find "Add Pattern to Intent" section
2. Select your new intent from dropdown
3. **Pattern**: Add different ways users might ask (one at a time):
   - "weather"
   - "mausam kaisa hai"
   - "temperature"
   - "is it raining"
4. Click **"Add Pattern"** for each

#### Step 4: Add Multiple Responses
1. Find "Add Response to Intent" section
2. Select your intent from dropdown
3. **Response**: Add different responses:
   - "It's sunny today!"
   - "Weather is great!"
   - "Perfect day outside!"
4. Click **"Add Response"** for each

#### Step 5: Retrain Model
1. Click **"🧠 Train AI Model"** button
2. Wait for training to complete
3. Test your new intent in chat

### Example: Adding "Weather" Intent

#### Intent Creation:
```
Tag: weather
Response: It's sunny today!
```

#### Patterns to Add:
- weather
- mausam
- temperature  
- aaj ka mausam
- how is the weather
- is it hot outside

#### Responses to Add:
- It's sunny today! 🌞
- Weather is pleasant!
- Perfect day for outdoor activities!
- Temperature is around 25°C.

#### Testing:
After training, try in chat:
```
You: weather
AI: It's sunny today! 🌞 🎯 High Confidence: 89.4%

You: mausam kaisa hai
AI: Weather is pleasant! 🤔 Medium Confidence: 76.2%
```

## 5. Managing Existing Data

### Editing Intents
1. In admin panel, find intent in table
2. Click on the tag or response to edit
3. Type new value
4. Click **"Update"** button

### Adding More Patterns
1. Select intent from "Add Pattern" dropdown
2. Type new pattern
3. Click **"Add Pattern"**
4. Retrain model for best results

### Adding More Responses
1. Select intent from "Add Response" dropdown  
2. Type new response
3. Click **"Add Response"**
4. AI will randomly choose from available responses

### Deleting Items
⚠️ **Be careful! Deleting intents removes all patterns and responses**

1. Click **"Delete"** button next to item
2. Confirm the deletion
3. Retrain model if needed

## 6. Viewing Chat History

### Access Chat Logs
1. Go to: http://localhost:5000/chatlog
2. See all conversation history
3. Shows user messages and AI responses
4. Includes timestamps

### Uses for Chat History:
- See what users are asking
- Identify missing intents
- Improve AI responses
- Monitor system usage

## 7. Troubleshooting Common Issues

### "Model is not trained yet" Error
**Solution**: Train the model first
1. Go to admin panel
2. Click "Train AI Model"
3. Wait for completion

### Low Confidence Responses
**Solutions**:
- Add more patterns per intent (minimum 5-10)
- Use diverse ways of asking same thing
- Include both English and Hinglish
- Retrain model after adding data

### AI Gives Wrong Responses
**Solutions**:
- Check if patterns are correct for intent
- Add more specific patterns
- Separate similar intents
- Improve response quality

### Admin Panel Not Working
**Solutions**:
- Check if Flask app is running
- Verify database connection
- Refresh the page

## 8. Best Practices for Good AI Performance

### Pattern Quality
✅ **Good Patterns**:
- "fees kitne hain"
- "course price kya hai"
- "admission charges"

❌ **Bad Patterns**:
- "abc"
- "123"
- Single letters

### Response Variety
✅ **Good Responses** (multiple per intent):
- "Our course fee is ₹5000"
- "Fees start from ₹3000"
- "Please call for fee details"

❌ **Bad Responses** (single or generic):
- "Yes"
- "Okay"
- "Got it"

### Intent Categories
✅ **Good Intents**:
- Specific: "fees", "appointment", "admission"
- Clear purpose
- Distinct from each other

❌ **Bad Intents**:
- Too general: "help", "info"
- Overlapping categories
- Vague purposes

## 9. Advanced Usage Tips

### Improving Accuracy
1. **Add 5-10 patterns per intent minimum**
2. **Include both English and Hinglish**
3. **Use different sentence structures**
4. **Add common typos and variations**
5. **Retrain after major changes**

### Monitoring Performance
1. **Check confidence scores regularly**
2. **Review chat history weekly**
3. **Add missing intents based on user questions**
4. **Update responses to be more helpful**

### Scaling Up
1. **Start with 5-10 core intents**
2. **Gradually add more categories**
3. **Maintain quality over quantity**
4. **Regular maintenance and updates**

## 10. Quick Reference

### Common Commands
```bash
# Start application
python app.py

# Open admin panel
http://localhost:5000/admin

# Train model (in admin)
Click "🧠 Train AI Model"

# View chat history  
http://localhost:5000/chatlog
```

### Sample Test Messages
- "hello" → Greeting
- "fees" → Fee information
- "appointment" → Appointment booking
- "thanks" → Thank you response
- "bye" → Goodbye message

### Confidence Meaning
- 🟢 **80%+**: Very confident
- 🟡 **60-79%**: Somewhat confident
- 🔴 **<60%**: Not confident, fallback response

---

## 🎉 You're Ready to Go!

You now have a fully functional AI chatbot with:
- ✅ Deep learning intent classification
- ✅ Confidence scoring
- ✅ Multiple responses per intent
- ✅ Admin panel for management
- ✅ Easy training and updates

Start with basic intents, train the model, and gradually expand your AI's capabilities!

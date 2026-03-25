-- Sample data for Part 3 AI Chatbot
INSERT INTO intents (tag) VALUES 
('greeting'), ('goodbye'), ('fees'), ('appointment'), ('thanks'), ('default');

INSERT INTO responses (intent_id, response_text) VALUES 
(1, 'Hello! How can I help you today?'), 
(1, 'Hi there! Welcome!'), 
(1, 'Namaste! Kya kaam hai?'),
(2, 'Goodbye! Have a great day!'), 
(2, 'Bye bye! See you later!'), 
(2, 'Alvida! Milte hain!'),
(3, 'Our course fee is ₹5000 for 3 months.'), 
(3, 'Fees structure: Basic - ₹3000, Advanced - ₹5000.'), 
(3, 'Please call office for detailed fee information.'),
(4, 'You can book appointment by calling 9876543210.'), 
(4, 'Visit our office between 10AM-6PM for appointment.'), 
(4, 'Appointment booked! Please come tomorrow.'),
(5, 'You are welcome!'), 
(5, 'No problem! Happy to help!'), 
(5, 'Pleasure is all mine!'),
(6, 'I did not understand that. Can you try again?'), 
(6, 'Sorry, please rephrase your question.');

INSERT INTO patterns (intent_id, pattern) VALUES 
(1, 'hello'), (1, 'hi'), (1, 'namaste'), (1, 'kya haal hai'), (1, 'good morning'),
(2, 'bye'), (2, 'goodbye'), (2, 'see you'), (2, 'alvida'), (2, 'ja raha hoon'),
(3, 'fees'), (3, 'kitne paise'), (3, 'course fee'), (3, 'price'), (3, 'cost'),
(4, 'appointment'), (4, 'book appointment'), (4, 'meeting'), (4, 'milna hai'), (4, 'time chahiye'),
(5, 'thanks'), (5, 'thank you'), (5, 'dhanyawad'), (5, 'shukriya'), (5, 'bahut accha'),
(6, 'help'), (6, 'what'), (6, 'how'), (6, 'tell me'), (6, 'pata nahi');

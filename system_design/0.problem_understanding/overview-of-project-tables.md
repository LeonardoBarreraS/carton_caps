# Overview of Project Tables

The dataset contains 5 tables:

1. Users  
2. Schools  
3. Products  
4. Purchase_History  
5. Conversation_History  

Together they model:

Users → support → Schools  
Users → buy → Products  
Users → talk → Assistant  

---

# 1. Users table

Represents parents using the app

Fields:

- id
- school_id
- name
- email
- created_at

Key meaning:

- Each user is linked to one school
- This defines who they support
- This is the fundraising relationship

Example:

User → supports Lincoln School

---

# 2. Schools table

Represents schools receiving donations

Fields:

- id
- name
- address
- created_at

Key meaning:

- Users choose one school
- Donations tied to this entity

Relationship:

Users.school_id → Schools.id

This creates:

User → supports → School

---

# 3. Products table

Represents everyday grocery products

Fields:

- id
- name
- description
- price
- created_at

Examples:

- cereal
- snacks
- oatmeal
- mac & cheese

Key meaning:

- products users buy
- purchases generate donations
- assistant recommends from this table

This is the recommendation catalog.

---

# 4. Purchase_History table

Represents user purchases

Fields:

- id
- user_id
- product_id
- quantity
- purchased_at

Relationships:

Users.id → user_id  
Products.id → product_id  

This connects:

User → bought → Product

Important observation:

This table is empty

Meaning:

- no historical purchases
- recommendations cannot rely on behavior
- assistant must rely on conversation context

---

# 5. Conversation_History table

Represents chat messages

Fields:

- id
- user_id
- message
- sender (user / bot)
- timestamp

This is interaction memory.

Allows:

- multi-turn conversation
- preference extraction
- contextual recommendations

This is primary personalization signal.

---

# Relationship Diagram (Conceptual)

Users → belongs to → Schools  
Users → buys → Products (via Purchase_History)  
Users → chats with → Assistant (via Conversation_History)

---

# What this data enables

From Users:
- know supported school

From Products:
- recommend items

From Conversations:
- infer preferences

From Purchases (future):
- learn behavior

---

# Key Observations

1. Small product catalog → simple recommendation scope  
2. No purchase history → conversational recommendations required  
3. Users linked to schools → fundraising context exists  
4. Conversation history present → multi-turn reasoning expected  
5. Simple schema → prototype-level design  

---

# One sentence summary

Dataset models users supporting schools, browsing products, and chatting with assistant that must use conversation context to guide purchasing decisions that drive fundraising.
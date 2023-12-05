import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import re
import tokenizermodule as tm


# Import training and test data
train = pd.read_excel(r'C:\Users\EkeleOgbadu\Documents\Scout_Data_Experiment\bagofwords\train.xlsx')
test = pd.read_excel(r'C:\Users\EkeleOgbadu\Documents\Scout_Data_Experiment\bagofwords\test.xlsx')

# Get the number of sentences in the training data
num_sentences = train["Commander"].size

# Clean and parse the training set
print ("Cleaning and parsing the training set\n")
clean_train = []
for i in range( 0, len(train["Commander"])):
    if( (i+1)%100 == 0 ):
        print ("Sentence %d of %d\n" % ( i+1, num_sentences )  )  

    clean_train.append(" ".join(tm.processSentence(train["Commander"][i])))

# Print the top 5 sentences on the training set
print(clean_train[:5])

# Create the bag of words model for the training set, , and convert to a numpy array
print ("Creating the bag of words...\n")
vectorizer = CountVectorizer()
train_data_features = vectorizer.fit_transform(clean_train)
train_data_features = train_data_features.toarray()


print ("Training the random forest (this may take a while)...")

# Initialize a Random Forest classifier with 100 trees
forest = RandomForestClassifier(n_estimators = 100)

# Fit the forest to the training set, using the bag of words as
# features and the Dialogue Move labels as the response variable
#
# This may take a few minutes to run
forest = forest.fit( train_data_features, train["Dialogue Move"] )


# Clean and parse the test set
clean_test = []

print ("Cleaning and parsing the test set...\n")
for i in range(0,len(test["Commander"])):
    clean_test.append(" ".join(tm.processSentence(test["Commander"][i])))


# Get a bag of words for the test set, and convert to a numpy array
test_data_features = vectorizer.transform(clean_test)
test_data_features = test_data_features.toarray()


# Use the random forest to make Dialogue Move label predictions
print ("Predicting test labels...\n")
result = forest.predict(test_data_features)

# Copy the results to a pandas dataframe with an "Commander" column, "Original" and
# a "Predicted" columns
output = pd.DataFrame( data={"Commander":test["Commander"], "Original":test["Dialogue Move"], "Prediction":result} )
#output = pd.DataFrame( data={"Commander":clean_test, "Original":test["Dialogue Move"], "Prediction":result} )

# Use pandas to write the comma-separated output file
output.to_excel('Bag_of_Words_model.xlsx', index=False)
print ("Wrote results to Bag_of_Words_model.xlsx")






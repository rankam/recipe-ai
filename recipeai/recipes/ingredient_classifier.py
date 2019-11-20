import fasttext

model = fasttext.load_model('/users/aaronrank/developer/recipe-ai/recipeai/recipes/.ingredient_classifier_model')

def predict(text):
    '''Returns label, confidence'''
    clf = model.predict(text)
    return clf[0][0], clf[1][0]




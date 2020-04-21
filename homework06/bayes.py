class NaiveBayesClassifier:

    def __init__(self, alpha=0.05):
        self.alpha = alpha
        self.words = {}
        self.words_prob = {}
        self.predicted = {'good': 0, 'maybe': 0, 'never': 0}
        self.class_distinct = {'good': 0, 'maybe': 0, 'never': 0, 'all': 0}

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        for i in range(len(X)):
            for word in X[i].split():
                self.class_distinct[y[i]] += 1
                self.class_distinct['all'] += 1
                if word in set(self.words.keys()):
                    self.words[word][y[i]] += 1
                    self.words[word]['all'] += 1
                else:
                    self.words[word] = {'good': 0, 'maybe': 0, 'never': 0, 'all': 1}
                    self.words[word][y[i]] += 1

        for word in self.words.keys():
            good_prob = (self.words[word]['good'] + self.alpha) / (
                    self.words[word]['all'] + self.alpha * self.class_distinct['good'])

            maybe_prob = (self.words[word]['maybe'] + self.alpha) / (
                    self.words[word]['all'] + self.alpha * self.class_distinct['maybe'])

            never_prob = (self.words[word]['never'] + self.alpha) / (
                    self.words[word]['all'] + self.alpha * self.class_distinct['never'])

            self.words_prob[word] = {
                'good': good_prob,
                'maybe': maybe_prob,
                'never': never_prob
            }

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        summ = [0, 0, 0]
        res = ['good', 'maybe', 'never']
        for word in X:
            if word in set(self.words_prob.keys()):
                summ[0] += self.words_prob[word]['good']
                summ[1] += self.words_prob[word]['maybe']
                summ[2] += self.words_prob[word]['never']
        return res[summ.index(max(summ))]

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        results = {'all': 0, 'right': 0}
        for i in range(len(X_test)):
            results['all'] += 1
            if self.predict(X_test[i]) == y_test[i]:
                results['right'] += 1
        return results['right'] / results['all']

#
# with open("data/SMSSpamCollection") as f:
#     data = list(csv.reader(f, delimiter="\t"))
#
#
# def clean(s):
#     translator = str.maketrans("", "", string.punctuation)
#     return s.translate(translator)
#
#
# X, y = [], []
# for target, msg in data:
#     X.append(msg)
#     y.append(target)
#
# X = [clean(x).lower() for x in X]
#
# X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
#
# model = NaiveBayesClassifier()
# model.fit(X_train, y_train)
#
# print(model.score(X_test, y_test))
#
# model3 = Pipeline([
#     ('vectorizer', TfidfVectorizer()),
#     ('classifier', MultinomialNB(alpha=0.05)),
# ])
#
# model3.fit(X_train, y_train)
# print(model3.score(X_test, y_test))
# # 0.982057416268

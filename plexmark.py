import os, sys, time, requests, markovify
import simplejson as json

def main(args):
    if args:
        model = MText(all_exes_in_uid(args[0]))
        for _ in range(30):
            print(model.make_sentence(tries=100))
    else:
        print('input missing: language variety')


# custom sentence splitting function for single exps instead of sentences
class MText(markovify.Text):
    def sentence_split(self, text):
        split = super().sentence_split(text)
        result = []
        for l in split:
            for s in l.split('\n'):
                result.append(s)
        return result
    
    def word_split(self, sentence):
        return list(sentence)
    
    def word_join(self, words):
        return "".join(words)


def all_exes_in_uid(uid):
    assert len(uid) in (3,7)
    if len(uid) == 3: uid += '-000'

    # test for cached file
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', '{}.txt'.format(uid)), 'r') as inf:
            return inf.read()
    except:
        # get list from api
        data = { "uid" : uid, "after" : 0 }
        request = { "resultNum" : 2000 }
        expressions = []
        while request["resultNum"] == 2000:
            r = requests.post('https://api.panlex.org/ex', data=json.dumps(data))
            request = json.loads(str(r.content, 'utf-8'), encoding='utf-8')
            time.sleep(0.5)
            if 'result' in request:
                expressions += [r['tt'] for r in request['result']]
                print('fetched {} exps → {}'.format(request['resultNum'], len(expressions)))
                data['after'] = request['result'][-1]['ex']
            else:
                print(request)
        exps_joined = "\n".join(expressions)
        with open(os.path.join(os.path.dirname(__file__), 'data', '{}.txt'.format(uid)), 'w') as outf:
            outf.write(exps_joined)
        return exps_joined


if __name__ == '__main__':
    main(sys.argv[1:])

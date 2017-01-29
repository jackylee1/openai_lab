
# 1.
# a) must construct experiment fro inside the f. This is so we can try continuous range of param by sampling from space
# b) run experiment from end to end, for good design
# c) from trials, return the data and aggregate for metrics_df
# 2. to run end to end, i.e. do a) and b) above, we need experiment_id (and other non-sess_spec variables) to be set from the f
# 3. param (sess_spec) space should really set params(sess_specs) only, for clean design and ability to do search properly. use a global counter (shared across processes in case of parallel runs) to set the experiment_num and anything else. A central counter that increases the global variables, call that source a global_variable_source
# 4. ok fuck have to do space enumeration on param, so sess_spec would
# have to go in gvs

import copy
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials


class GlobalVariableSource(object):

    '''
    the global variable source (gvs) basic implementation
    allows sharing of variables across processes
    '''

    def __init__(self, **kwargs):
        self.REQUIRED_GLOBAL_VARS = [
            'common_sess_spec',
            'times',
            'experiment_num',
            'num_of_experiments',
            'run_timestamp'
        ]
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self.common_sess_spec.pop('param', None)
        self.common_sess_spec.pop('param_range', None)
        assert all(k in kwargs for k in REQUIRED_SYS_KEYS)

    def increment(self):
        self.experiment_num += 1

    def get_next(self):
        self.increment()
        return self.__dict__


# gv_seed = {
#     'common_sess_spec': sess_spec,
#     'times': times,
#     'experiment_num': 0,
#     'num_of_experiments': max_evals,
#     'run_timestamp': timestamp()
# }
# gvs = GlobalVariableSource(gv_seed)

#######
#######
#######
# param_space = generate_param_space(sess_spec)
# f
# trials = Trials()
# best = fmin(fn=f, space=fspace, algo=tpe.suggest, max_evals=50, trials=trials)

# gvs = {'SOME': 'PROPER CLASS OBJECT'}
# uses gvs in param space generation
# param_space = generate_param_space(sess_spec)


def convert_to_hp(k, v):
    '''
    convert to hyperopt param expressions. refer:
    https://github.com/hyperopt/hyperopt/wiki/FMin#21-parameter-expressions
    param = {
        'learning_rate': {
            'uniform': {
                'low': 0.0001,
                'high': 1.0
            }
        },
        'hidden_layers_activation': ['relu', 'linear']
    }
    for k in param:
        v = param[k]
        print(convert_to_hp(k, v))
    '''
    if isinstance(v, list):
        return hp.choice(k, v)
    elif isinstance(v, dict):
        space_keys = list(v.keys())
        assert len(space_keys) == 1
        space_k = space_keys[0]
        space_v = v[space_k]
        space = getattr(hp, space_k)(k, **space_v)
        return space
    else:
        raise TypeError('sess_spec param_range value must be a list or dict')


# generate param_space for hyperopt from sess_spec
def generate_param_space(sess_spec):
    assert 'param' in sess_spec
    assert 'param_range' in sess_spec
    default_param = sess_spec['param']
    param_space = copy.copy(default_param)
    param_range = sess_spec['param_range']
    for k in param_range:
        v = param_range[k]
        space = convert_to_hp(k, v)
        param_space[k] = space
    return param_space


# SOLID
def hyperopt_run_experiment(param):
    # use param to carry those params other than sess_spec
    # set a global gvs: global variable source
    gv = gvs.get_next()
    sess_spec = gv['common_sess_spec']
    sess_spec.update({'param': param})
    times = gv['times']
    experiment_num = gv['experiment_num']
    num_of_experiments = gv['num_of_experiments']
    run_timestamp = gv['run_timestamp']

    experiment = Experiment(
        sess_spec,
        times=times,
        experiment_num=experiment_num,
        num_of_experiments=num_of_experiments,
        run_timestamp=run_timestamp)
    experiment_data = experiment.run()
    metrics = experiment_data['summary']['metrics']
    # to maximize avg mean rewards/epi via minimization
    hyperopt_loss = -1. * metrics['mean_rewards_per_epi_stats']['mean']
    return {'loss': hyperopt_loss,
            'status': STATUS_OK,
            'experiment_data': experiment_data}


def hyperopt_analyze_param_space(trials):
    # recover experiment_data_array
    experiment_data_array = []
    return analyze_param_space(experiment_data_array)


# fspace = {
#     'x': hp.uniform('x', -5, 5)
# }


# def f(params):
#     x = params['x']
#     val = x**2
#     return {'loss': val, 'status': STATUS_OK}

# trials = Trials()
#     best = fmin(
#         fn=f, space=fspace, algo=tpe.suggest, max_evals=50, trials=trials)

# print 'best:', best

# print 'trials:'
# for trial in trials.trials[:2]:
#     print trial


# param_space = param_to_hp(param)


# def f(param):
#     # form sess_spec with param
#     # define loss as high level wrapper for experiment analyze_param_space
#     # spec algo, run
#     return


# from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

# fspace = {
#     'x': hp.uniform('x', -5, 5),
#     'w': hp.uniform('w', 0, 2),
# }


# def f(params):
#     print(params)
#     x = params['x']
#     w = params['w']
#     # print(w)
#     val = x**2 + w
#     return {'loss': val, 'status': STATUS_OK}

# trials = Trials()
# best = fmin(fn=f, space=fspace, algo=tpe.suggest, max_evals=50, trials=trials)

# print('best:')
# print(best)

# print('trials:')
# for trial in trials.trials[:2]:
#     print(trial)

# {'book_time': datetime.datetime(2017, 1, 27, 13, 43, 9, 843000), 'version': 0, 'misc': {'workdir': None, 'idxs': {'w': [0], 'x': [0]}, 'vals': {'w': [1.0731576319659286], 'x': [4.513243557043472]}, 'cmd': ('domain_attachment', 'FMinIter_Domain'), 'tid': 0}, 'spec': None, 'owner': None, 'exp_key': None, 'result': {'loss': 21.442525037160337, 'status': 'ok'}, 'refresh_time': datetime.datetime(2017, 1, 27, 13, 43, 9, 843000), 'state': 2, 'tid': 0}
# {'book_time': datetime.datetime(2017, 1, 27, 13, 43, 9, 845000), 'version': 0, 'misc': {'workdir': None, 'idxs': {'w': [1], 'x': [1]}, 'vals': {'w': [1.0203132874543943], 'x': [0.25778683285176385]}, 'cmd': ('domain_attachment', 'FMinIter_Domain'), 'tid': 1}, 'spec': None, 'owner': None, 'exp_key': None, 'result': {'loss': 1.0867673386461376, 'status': 'ok'}, 'refresh_time': datetime.datetime(2017, 1, 27, 13, 43, 9, 845000), 'state': 2, 'tid': 1}

# {'spec': None, 'misc': {'cmd': ('domain_attachment', 'FMinIter_Domain'), 'idxs': {'x': [0]}, 'workdir': None, 'vals': {'x': [-3.3728112348355763]}, 'tid': 0}, 'tid': 0, 'result': {'status': 'ok', 'loss': 12.375855625833085}, 'refresh_time': datetime.datetime(2017, 1, 27, 13, 37, 11, 258000), 'book_time': datetime.datetime(2017, 1, 27, 13, 37, 11, 258000), 'version': 0, 'state': 2, 'exp_key': None, 'owner': None}
# {'spec': None, 'misc': {'cmd': ('domain_attachment', 'FMinIter_Domain'), 'idxs': {'x': [1]}, 'workdir': None, 'vals': {'x': [-3.0197970008472996]}, 'tid': 1}, 'tid': 1, 'result': {'status': 'ok', 'loss': 10.119173926326345}, 'refresh_time': datetime.datetime(2017, 1, 27, 13, 37, 11, 259000), 'book_time': datetime.datetime(2017, 1, 27, 13, 37, 11, 259000), 'version': 0, 'state': 2, 'exp_key': None, 'owner': None}

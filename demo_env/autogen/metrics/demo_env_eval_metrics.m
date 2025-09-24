function demo_env_eval_metrics(name, varargin)
    eval(strcat(name, '(varargin{:})'));
end
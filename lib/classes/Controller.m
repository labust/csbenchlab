classdef (Abstract) Controller
    %CONTROLLER Base class for all controllers
    
    properties (Abstract, Constant)
       param_description
    end

    properties
        params
        input_size
        output_size
        data
        iid
        pid
        is_configured_v
        is_simulink
    end

    methods (Abstract)
       % called right after parameters and sizes have been set to configure
       % the class 
       on_configure(this); 
       % called every step to produce new output for the system
       on_step(this, y_ref, y, dt, varargin);

       % called to reset the controller behavior
       on_reset(this);
    end

    methods
        function this = Controller(args)
            this.is_configured_v = 0;
            begin_idx = 1;
            pid = double(0); iid = double(0); is_simulink = double(0);
            for i = begin_idx:2:length(args)

                if isstring(args{i})
                    as_char = convertStringsToChars(args{i});
                else
                    as_char = args{i};
                end

                value = args{i+1};
                switch as_char
                    case 'Dims'
                        validate_dims_struct(value);
                        data = this.create_data_model(this.params, value);
                    case 'Data'
                        data = value;
                    case 'Params'
                        params = value;
                    case 'iid'
                        iid = double(value);
                    case 'pid'
                        pid = double(value);
                    case 'is_simulink'
                        is_simulink = double(value);
                    otherwise
                        warning(['Unexpected parameter name "', as_char, '"']);
                end
            end
            if isempty(data)
                error("Data not set");
            end
            if isempty(params)
                error("Params not set");
            end
            this.is_simulink = is_simulink;
            this.params = params;
            this.data = data;
            this.iid = iid;
            this.pid = pid;
        end

        function this = configure(this, varargin)

            u_ic = varargin{1};
            simulink_in_size = 0;
            if nargin > 2
                simulink_in_size = varargin{2};
            end

            if nargin > 3
                ref_size = varargin{3};
                if ref_size(end) ~= simulink_in_size(1)
                    error('Dimensions of y and y_ref not consistent..');
                end
            end

            this = on_configure(this);
            this.is_configured_v = 1;
        end

        function [this, u] = step(this, y_ref, y, dt, varargin)
            [this, u] = on_step(this, y_ref, y, dt, varargin{:});
        end

        function this = override_params(this, params)
            this.params = params;
        end

        function this = reset(this)
            this = on_reset(this);
        end

        function t = is_configured(this)
            t = this.is_configured_v;
        end

    end
end


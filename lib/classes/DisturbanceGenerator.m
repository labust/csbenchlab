classdef (Abstract) DisturbanceGenerator
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
    end

    methods (Abstract)
       % called right after parameters and sizes have been set to configure
       % the class 
       on_configure(this); 
       % called every step to produce new output for the system
       on_step(this, y, dt, varargin);

       % called to reset the controller behavior
       on_reset(this);
    end

    methods
        function this = DisturbanceGenerator(args)
            begin_idx = 1;
            pid = 0; iid = 0;
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
                        this.data = this.create_data_model(this.params, value);
                    case 'Params'
                        params = value;
                    case 'Data'
                        data = value;
                    case 'iid'
                        iid = value;
                    case 'pid'
                        pid = value;
                    otherwise
                        warning(['Unexpected parameter name "', as_char, '"']);
                end
            end
            if isempty(params)
                error("Params not set");
            end
            if isempty(data)
                error("Data not set");
            end

            this.params = params;
            this.data = data;
            this.pid = pid;
            this.iid = iid;
        end
        
        function this = configure(this, varargin)
            is_simulink = 0;
            if nargin > 1
                is_simulink = varargin{1};
            end

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
        end

        function [this, u] = step(this, y, dt, varargin)
            [this, u] = on_step(this, y, dt, varargin{:});
        end

        function this = reset(this)
            this = on_reset(this);
        end

    end
end


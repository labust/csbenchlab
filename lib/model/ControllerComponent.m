classdef ControllerComponent < ComponentOptions
    %CONTROLLEROPTIONS Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        Mux
        RefHorizon
        RegenerateEnv
    end
    
    methods
        function obj = ControllerComponent(varargin)
            obj = obj@ComponentOptions(varargin{:});
            begin_idx = 1;
            if nargin > 0 && isa(varargin{1}, 'ControllerComponent')
                obj = varargin{1};
                begin_idx = 2;
            else
                obj.Mux.Inputs = [];
                obj.Mux.Outputs = [];
                obj.RegenerateEnv = 0;
                obj.RefHorizon = 1;
            end

               % Loop through the parameter names and not the values.
            for i = begin_idx:2:length(varargin)

                if isstring(varargin{i})
                    as_char = convertStringsToChars(varargin{i});
                else
                    as_char = varargin{i};
                end
                value = varargin{i+1};


                obj = set_value(obj, as_char, value);

            end

        end

        function obj = set_value(obj, name, value)
            switch name
                case 'Name' 
                    obj.Name = value;
                case 'Type'
                    obj.Type = value;  
                case 'Lib'
                    obj.Lib = value;      
                case 'Params'
                    obj.Params = value;
                case 'ParamsStructName'
                    obj.ParamsStructName = value;
                case 'Mux'
                    obj.Mux = value;
                case 'RefHorizon'
                    obj.RefHorizon = value;
                case 'RegenerateEnv'
                    obj.RegenerateEnv = value;
                case 'LibVersion'
                    obj.LibVersion = value;
                otherwise
                    warning(['Unexpected parameter name "', name, '"']);
            end
        end

        
    end
end


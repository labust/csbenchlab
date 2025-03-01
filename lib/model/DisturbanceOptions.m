classdef DisturbanceOptions < ComponentOptions
    %CONTROLLEROPTIONS Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
       
    end
    
    methods
        function obj = DisturbanceOptions(varargin)
            obj = obj@ComponentOptions(varargin{:});

            begin_idx = 1;
            if nargin > 0 && isa(varargin{1}, 'DisturbanceOptions')
                obj = varargin{1};
                begin_idx = 2;
            else
            end

            %    % Loop through the parameter names and not the values.
            % for i = begin_idx:2:length(varargin)
            % 
            %     if isstring(varargin{i})
            %         as_char = convertStringsToChars(varargin{i});
            %     else
            %         as_char = varargin{i};
            %     end
            %     value = varargin{i+1};
            %     obj = set_value(obj, as_char, value);
            % end

        end

        function obj = set_value(obj, name, value)
            switch name
                otherwise
                    warning(['Unexpected parameter name "', name, '"']);
            end
        end

        
    end
end


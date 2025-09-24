function [data_n,  u] = fcn_1a1e0224554d46b98b92911a9a843c5a_ext(y_ref, y, dt, u_ic, params, data, pid__, iid__)

    persistent comp_dict
    if isempty(comp_dict)
        comp_dict = dictionary;
    end

    iid = char(iid__);
    if comp_dict.numEntries == 0 || ...
        ~comp_dict.isKey(iid)
        o = PyComponentManager.instantiate_component('Controller2', 'test_lib', 'Params', params, 'Data', data, 'pid', pid__, 'iid', iid__);
        o.configure(u_ic, size(y), size(y_ref));
        comp_dict(iid) = o;
    else
        o = comp_dict(iid);
    end
    
    result = o.step(y_ref, y, dt);
    u = double(result)';
    data_n = py_parse_component_data(o.data);
    comp_dict(iid) = o;
end


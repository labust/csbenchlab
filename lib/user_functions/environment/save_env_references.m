function save_env_references(env_path, references)
    if ~is_env_path(env_path)
        [env_path, ~, ~] = fileparts(which(env_path));
    end
    validate_references(references);
    [~, name, ~] = fileparts(env_path);
    ref_path = fullfile(env_path, 'autogen', strcat(name, '_refs.mat'));

    names = {};
    for i=1:references.numElements
        names{end+1} = references{i}.Name;
        ds = Simulink.SimulationData.Dataset;
        ds = ds.addElement(references{i});
        eval(strcat(references{i}.Name, ' = ds;'));
    end
    save(ref_path, names{:});
end
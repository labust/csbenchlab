function out_with_ref(out, plot_cfg, f_handle)
    
    if ~exist('f_handle', 'var')
        f = figure;  
    else
        f = f_handle;
        set(0, 'CurrentFigure', f_handle)
    end

    hold on; 

    if is_valid_field(plot_cfg.Params, 'Grid')
        grid on;
    end

    if is_valid_field(plot_cfg, 'Name')
        set(f, 'Name',  plot_cfg.Name);
    end

    lw = 1;
    if is_valid_field(plot_cfg.Params, 'LineWidth')
        lw = plot_cfg.Params.LineWidth;
    end
    
    
    if is_valid_field(plot_cfg.Params, 'RefDimensions')
        ref_dims = plot_cfg.Params.RefDimensions;
    else
        ref_dim = size(out.ref.Data, 2);
        ref_dims = linspace(1, ref_dim, ref_dim);
    end

    if is_valid_field(plot_cfg.Params, 'OutDimensions')
        out_dims = plot_cfg.Params.OutDimensions;
    else
        fns = fieldnames(out.y);
        out_dim = size(out.y.(fns{1}).Data, 2);
        out_dims = linspace(1, out_dim, out_dim);
    end



    plot(out.ref.Time, out.ref.Data(:, ref_dims), 'LineWidth', lw, 'LineStyle', '--');
    
    if isfield(plot_cfg.Params, 'Controllers')
        names = plot_cfg.Params.Controllers;
    else
        names = fieldnames(out.y);
    end
    for i=1:length(names)
        n = names{i};
        data = out.y.(n);
        sz = size(data.Data);
        if sz(end) == length(data.Data)
            plot(data.Time, squeeze(data.Data(out_dims, :, :)), 'LineWidth', lw);
        else
            plot(data.Time, squeeze(data.Data(:, out_dims)), 'LineWidth', lw);
        end
    end

    if is_valid_field(plot_cfg.Params, 'Axis')
        axis(plot_cfg.Params.Axis);
    end 

    if is_valid_field(plot_cfg.Params, 'Position')
        set(gcf, 'Position',  plot_cfg.Params.Position);
    end 

    if is_valid_field(plot_cfg.Params, 'XLabel')
        xlabel(plot_cfg.Params.XLabel);
    end

    if is_valid_field(plot_cfg.Params, 'YLabel')
        ylabel(plot_cfg.Params.YLabel);
    end

    if is_valid_field(plot_cfg.Params, 'Legend')
        legend(plot_cfg.Params.Legend{:});
    else
        leg_names = {};
        for i=1:length(ref_dims)
            leg_names{end+1} = strcat('Reference_', num2str(i));
        end
        fns = fieldnames(out.y);
        for i=1:length(fns)
            for j=1:length(out_dims)
                leg_names{end+1} = strcat(fns{i}, '_', num2str(j));
            end
        end
        legend(leg_names{:});
    end

end


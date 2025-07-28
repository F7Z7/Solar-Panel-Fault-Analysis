model = 'base_model_solar';
load_system(model);

irradiance_values = 100:100:1000;
temp_values = 2:2:50;
total_sim = numel(irradiance_values) * numel(temp_values);
results = NaN(total_sim, 4);
sim_no = 0;
success_count = 0;
error_count = 0;
for T = temp_values
    for Ir = irradiance_values
        sim_no = sim_no + 1;

        try
            bdclose('all');
            load_system(model);

            simIn = Simulink.SimulationInput(model);
            simIn = simIn.setVariable('Ir', Ir);
            simIn = simIn.setVariable('T', T);
            simIn = simIn.setModelParameter( ...
                'StartTime', '0', ...
                'StopTime', '0.5', ...
                'Solver', 'ode23tb', ...
                'MaxStep', '1e-4', ...
                'RelTol', '1e-3', ...
                'AbsTol', '1e-4' ...
            );

            simOut = sim(simIn);

            V_PV = NaN; I_PV = NaN;
            V_PV_data = simOut.get('V_PV');
            if isnumeric(V_PV_data) && ~isempty(V_PV_data)
                V_PV = V_PV_data(end);
            end

            I_PV_data = simOut.get('I_PV');
            if isnumeric(I_PV_data) && ~isempty(I_PV_data)
                I_PV = I_PV_data(end);
            end

            % Inside the try block after the initial failure or invalid output
if isnan(V_PV) || isnan(I_PV) || isinf(V_PV) || isinf(I_PV) || V_PV <= 0 || I_PV <= 0
    % Attempt stricter retry
    fprintf('⚠️  Invalid output at Ir=%4.0f T=%2.0f — Retrying with ode15s...\n', Ir, T);

    simIn_retry = Simulink.SimulationInput(model);
    simIn_retry = simIn_retry.setVariable('Ir', Ir);
    simIn_retry = simIn_retry.setVariable('T', T);
    simIn_retry = simIn_retry.setModelParameter( ...
        'StartTime', '0', ...
        'StopTime', '0.5', ...
        'Solver', 'ode15s', ...
        'MaxStep', '1e-5', ...
        'RelTol', '1e-4', ...
        'AbsTol', '1e-5' ...
    );

    try
        simOut_retry = sim(simIn_retry);
        V_PV_data = simOut_retry.get('V_PV');
        I_PV_data = simOut_retry.get('I_PV');

        if isnumeric(V_PV_data) && ~isempty(V_PV_data)
            V_PV = V_PV_data(end);
        end
        if isnumeric(I_PV_data) && ~isempty(I_PV_data)
            I_PV = I_PV_data(end);
        end

        if isnan(V_PV) || isnan(I_PV) || isinf(V_PV) || isinf(I_PV) || V_PV <= 0 || I_PV <= 0
            fprintf('❌ Retry also failed (V=%.2f I=%.2f)\n', V_PV, I_PV);
            error_count = error_count + 1;
        else
            fprintf('✅ Retry success: Ir=%4.0f T=%2.0f (V=%.2f I=%.2f)\n', Ir, T, V_PV, I_PV);
            success_count = success_count + 1;
        end
         catch ME_retry
        fprintf('❌ Retry simulation failed — Error: %s\n', ME_retry.message);
        V_PV = NaN;
        I_PV = NaN;
        error_count = error_count + 1;
    end
            else
                fprintf('Sim %3d/%3d: Ir=%4.0f T=%2.0f — Success (V=%.2f I=%.2f)\n', ...
                        sim_no, total_sim, Ir, T, V_PV, I_PV);
                success_count = success_count + 1;
            end

            results(sim_no, :) = [Ir, T, V_PV, I_PV];

        catch ME
            fprintf('Simulation failed at Ir=%4.0f, T=%2.0f — Error: %s\n', Ir, T, ME.message);
            results(sim_no, :) = [Ir, T, NaN, NaN];
            error_count = error_count + 1;
        end
    end
end
success_percentage = (success_count / total_sim) * 100;
fprintf('\nSimulation complete.\n');
fprintf('Total simulations: %d\n', total_sim);
fprintf('Successful simulations: %d\n', success_count);
fprintf('Failed simulations: %d\n', error_count);
fprintf('Success rate: %.2f%%\n', success_percentage);

resultTable = array2table(results, 'VariableNames', {'Irradiance', 'Temperature', 'V_PV', 'I_PV'});
writetable(resultTable, 'solar_sim_results.csv');
fprintf('Simulation complete. Results saved to solar_sim_final_results.csv\n');

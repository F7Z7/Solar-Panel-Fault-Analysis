model = 'base_model_solar';
load_system(model);

irradiance_values = 100:100:1000;
temp_values = 2:2:50;

total_sim = numel(irradiance_values) * numel(temp_values);
results = []; %for storing the vairable
sim_no = 0;

for T = temp_values
    for Ir = irradiance_values
        %this will iterate 
        sim_no = sim_no + 1;
        success = 0;
%first assign the values to workspace we use assign
        try
            % this will assign the values to the vars respectively 
            assignin("base", "Ir", Ir);
            assignin("base", "T", T);

            simOut = sim(model, ...
                'StartTime', '0', ...
                'StopTime', '0.5', ...
                'Solver', 'ode23tb', ...
                'MaxStep', '1e-4', ...
                'RelTol', '1e-3', ...
                'AbsTol', '1e-4');

            V_PV = NaN; I_PV = NaN; %assignin it to not a num

%etracting V_PV
            V_PV_data = simOut.get("V_PV");
%this chechks ig the values is 

            if isnumeric(V_PV_data) && ~isempty(V_PV_data)
                V_PV = V_PV_data(end);
            end

            I_PV_data = simOut.get("I_PV");
            if isnumeric(I_PV_data) && ~isempty(I_PV_data)
                I_PV = I_PV_data(end);
            end

            if isnan(V_PV) || isnan(I_PV) || isinf(V_PV) || isinf(I_PV) || V_PV <= 0 || I_PV <= 0
                fprintf('Invalid Output at (V=%.2f I=%.2f) for Ir=%4.0f T=%2.0f at SIM %3d/%3d\n', ...
                    V_PV, I_PV, Ir, T, sim_no, total_sim);
                results = [results; Ir, T, NaN, NaN];
            else
                fprintf('Sim %3d/%3d: Ir=%4.0f T=%2.0f — Success (V=%.2f I=%.2f)\n', ...
                    sim_no, total_sim, Ir, T, V_PV, I_PV);
                results = [results; Ir, T, V_PV, I_PV];
                success = success + 1;
            end

        catch ME
            fprintf('Simulation failed at Ir=%4.0f, T=%2.0f — Error: %s\n', Ir, T, ME.message);
            results = [results; Ir, T, NaN, NaN];
        end
    end
end

resultTable = array2table(results, 'VariableNames', {'Irradiance', 'Temperature', 'V_PV', 'I_PV'});
writetable(resultTable, 'solar_sim_results.csv');
fprintf('Simulation complete. Results saved to solar_sim_results.csv\n');

<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" name="Datacenter_BESS_Scenario" description="Datacenter with BESS and grid connection" id="9e6ef2f4-ebdb-449a-a98c-677753f56cdf">
  <instance xsi:type="esdl:Instance" id="3b05ea7a-281b-4aff-9eaa-d6b6752d00aa" name="scenario_instance">
    <area xsi:type="esdl:Area" id="6548897b-b73b-44fe-8986-ccf860afec3f" name="Datacenter_Site">
      <asset xsi:type="esdl:ElectricityNetwork" name="Site Electricity Management System" id="bab54f65-82dc-41b3-af8e-afae8238819f">
        <port xsi:type="esdl:OutPort" name="net_to_datacenter" id="7070a090-754a-42ce-b1a8-f2d1151c7e43" connectedTo="838118ab-2db5-4f4e-9579-078ac83a79ce"/>
        <port xsi:type="esdl:OutPort" name="net_to_bess" id="4f4bec2d-8ab1-4aeb-9b95-fcb9d078a9e8" connectedTo="a1086733-30f3-4f3d-9f6c-e0ab1044ef69"/>
        <port xsi:type="esdl:InPort" name="net_from_bess" id="eb272b68-df61-467c-ab2a-2896a7cefd02" connectedTo="79456d8f-f6ce-44e8-8657-cc04c395ad3b"/>
        <port xsi:type="esdl:OutPort" name="net_to_grid" id="d5e555aa-b1ac-4377-9803-063f9cf09316" connectedTo="a402a4ec-3b63-47a0-b766-3aeb25d6900b"/>
        <port xsi:type="esdl:InPort" name="net_from_grid" id="bb9bafb3-9d09-4914-af50-48c73ee01a4e" connectedTo="a21daa45-63a2-426e-b01f-da7e4a978bc0"/>
        <port xsi:type="esdl:InPort" name="net_from_backup_generator" id="b696eef7-43ba-46c4-bfd3-a455e921a39f" connectedTo="6f7dfd83-48ef-4eed-977f-f964a8e577ee"/>
        <port xsi:type="esdl:InPort" name="net_from_local_res" id="b38ae08a-5a1f-48b0-9ed6-399ca50f0eba" connectedTo="0109c6a3-9162-4996-99cf-4276c7d9c25b"/>
        <KPIs xsi:type="esdl:KPIs" id="1089cc12-58aa-4c0b-8512-5c17ad9bf573">
          <kpi xsi:type="esdl:DoubleKPI" name="w_unserved" value="1000000000.0" id="e9bd7797-e3dc-48b2-a97a-38731190ca94"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_carbon" value="1.0" id="1ddd3fb6-3895-474d-a7a6-26be7e8c09e7"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_price" value="1.0" id="4f9978af-39d8-41e6-942a-3fc5795ad59e"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_effort" value="0.01" id="86e3904f-5120-484c-926f-13d5dab8feb8"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_soc_low" value="1000000.0" id="01765cdd-1c14-4b10-b512-6994b6555283"/>
          <kpi xsi:type="esdl:DoubleKPI" name="soc_baseline" value="50.0" id="34f0fb81-8863-4ef6-a1a1-7cbaa78a9875"/>
          <kpi xsi:type="esdl:DoubleKPI" name="cfe_constraint_mode" id="097e4a9b-c1e0-476e-b583-3008b0812edf"/>
          <kpi xsi:type="esdl:DoubleKPI" name="cfe_min_fraction" id="ee88af1e-0014-4b2f-acfe-76f4f7849de9"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_battery" value="1.0" id="99ef7525-36e2-4f3a-b40b-da452d95f8a9"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_backup_generator" value="1.0" id="e9227ccb-f1bb-495d-a2e7-f900ec1a1747"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_renewable_service" value="1.0" id="5e36ce34-423d-4405-bf5f-b191147d1727"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_change_management" value="1.0" id="0c0857d8-0919-4030-951b-537429ee44d0"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_goal_management" value="1.0" id="197c8355-2dca-49b6-ad5c-2edec8a19359"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_mandate" value="1.0" id="d26f87be-ab12-4745-9f68-8f444a40cb6e"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_shared_transformer" value="1.0" id="baf5cdb2-c348-4791-b0d7-1441cb899bda"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_soc_drift_threshold" value="5.0" id="3a1448c7-e133-437f-b36b-b231347831f2"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_demand_spike_threshold" value="0.1" id="28312334-a906-4a62-b32b-881f88281bf8"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_horizon_steps" value="24.0" id="e1a31deb-f5ed-45f2-b19e-f52a2a508d32"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_replan_cooldown" value="4.0" id="febe6dbb-2c61-4b4b-a2db-6915ecf548a4"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_sigma_ci" value="0.12" id="218179fd-ed0e-4a0d-bbd2-b76e635cca74"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_sigma_p_dc" value="0.05" id="39566b3f-5040-4e19-a972-065ba3b8715b"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_sigma_price" value="0.15" id="d8e41a4a-fe37-4bfb-b630-9f60d60da948"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_seed" value="42.0" id="a2540a8d-2473-4d79-aa89-594eb4627f03"/>
          <kpi xsi:type="esdl:DoubleKPI" name="backup_co2_factor" value="600.0" id="68487946-f053-439f-9459-dc328aca192f"/>
          <kpi xsi:type="esdl:DoubleKPI" name="backup_cost_eur_per_kwh" value="0.4" id="798f9440-e520-4042-920e-372602d30d93"/>
          <kpi xsi:type="esdl:DoubleKPI" name="sim_seed" value="42.0" id="a59387b4-0537-4e38-94db-3d394ac8615e"/>
        </KPIs>
      </asset>
      <asset xsi:type="esdl:ElectricityDemand" powerFactor="0.95" name="Datacenter Load" power="4000000.0" id="923acc26-2ac1-4ed2-8851-e29f0e1510d8">
        <port xsi:type="esdl:InPort" id="838118ab-2db5-4f4e-9579-078ac83a79ce" name="dc_in" connectedTo="7070a090-754a-42ce-b1a8-f2d1151c7e43">
          <profile xsi:type="esdl:InfluxDBProfile" database="GO-e" host="influxdb" id="ce827582-03b5-4d69-b76c-cdcfacdeee3f" filters="name='Datacenter Load'" measurement="historical_datacenter_demand" port="8086" field="Demand_W"/>
        </port>
      </asset>
      <asset xsi:type="esdl:Battery" chargeEfficiency="0.95" capacity="4000000.0" name="Datacenter BESS" maxDischargeRate="4000000.0" maxChargeRate="4000000.0" id="5568e592-315c-4c38-93ec-e238f39ee069" dischargeEfficiency="0.95">
        <port xsi:type="esdl:InPort" name="bess_in" id="a1086733-30f3-4f3d-9f6c-e0ab1044ef69" connectedTo="4f4bec2d-8ab1-4aeb-9b95-fcb9d078a9e8"/>
        <port xsi:type="esdl:OutPort" name="bess_out" id="79456d8f-f6ce-44e8-8657-cc04c395ad3b" connectedTo="eb272b68-df61-467c-ab2a-2896a7cefd02"/>
      </asset>
      <asset xsi:type="esdl:PowerPlant" power="10000000.0" minLoad="-10000000" name="Grid Connection" efficiency="1.0" id="245e3314-8d34-492a-9e30-9e691bd5d984">
        <port xsi:type="esdl:InPort" id="a402a4ec-3b63-47a0-b766-3aeb25d6900b" name="grid_in" connectedTo="d5e555aa-b1ac-4377-9803-063f9cf09316">
          <profile xsi:type="esdl:InfluxDBProfile" database="GO-e" host="influxdb" id="c648e52b-0fcc-444b-a7c0-c3318b0d44a4" filters="name='Grid Connection'" measurement="transformer_background" port="8086" field="background_w"/>
          <profile xsi:type="esdl:InfluxDBProfile" database="GO-e" host="influxdb" id="9473b6b4-8276-4ab8-98ed-edece81a6b69" filters="name='Grid Connection'" measurement="carbon_intensity" port="8086" field="carbon_intensity"/>
          <profile xsi:type="esdl:InfluxDBProfile" database="GO-e" host="influxdb" id="6f215a0e-0a70-4281-ba95-b5a38878aae6" filters="name='Grid Connection'" measurement="carbon_intensity" port="8086" field="carbon_free_pct"/>
          <profile xsi:type="esdl:InfluxDBProfile" database="GO-e" host="influxdb" id="56ad61a0-14df-4074-98ab-bbb361dbd24f" filters="name='Grid Connection'" measurement="price-day-ahead" port="8086" field="price"/>
        </port>
        <port xsi:type="esdl:OutPort" name="grid_out" id="a21daa45-63a2-426e-b01f-da7e4a978bc0" connectedTo="bb9bafb3-9d09-4914-af50-48c73ee01a4e"/>
      </asset>
      <asset xsi:type="esdl:GasProducer" name="Backup Generator" power="5000000.0" id="437e6f20-beed-4f9b-978d-11f7c150e2ed">
        <port xsi:type="esdl:OutPort" name="gen_out" id="6f7dfd83-48ef-4eed-977f-f964a8e577ee" connectedTo="b696eef7-43ba-46c4-bfd3-a455e921a39f"/>
      </asset>
      <asset xsi:type="esdl:PVInstallation" angle="35" name="Local Renewable Energy Source" panelEfficiency="0.2" power="1000000.0" orientation="180" id="cf49f900-4cc7-4925-b97a-eef3afa6a7f5" surfaceArea="5000" inverterEfficiency="0.98">
        <port xsi:type="esdl:OutPort" connectedTo="b38ae08a-5a1f-48b0-9ed6-399ca50f0eba" id="0109c6a3-9162-4996-99cf-4276c7d9c25b" name="res_out">
          <profile xsi:type="esdl:InfluxDBProfile" database="GO-e" host="influxdb" id="d523de4f-c83b-4808-a9ad-99b87dde0345" filters="name='Local RES'" measurement="historical_solar_irradiance" port="8086" field="Irradiance_W_m2"/>
        </port>
      </asset>
    </area>
  </instance>
</esdl:EnergySystem>

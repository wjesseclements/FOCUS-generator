import React, { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Calendar, AlertCircle } from "lucide-react";
import CloudProviderSelector from "../ui/CloudProviderSelector";
import { Card, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import Tooltip from "../ui/Tooltip";
import { toast } from "sonner";

const scenarios = [
  {
    id: "linear",
    name: "Linear Growth",
    description: "Steady, predictable growth over time",
    icon: TrendingUp,
    parameters: [
      { id: "growthRate", label: "Monthly Growth Rate (%)", type: "number", min: 0, max: 50, default: 10 }
    ]
  },
  {
    id: "seasonal",
    name: "Seasonal Patterns",
    description: "Recurring spikes for holidays, events, or business cycles",
    icon: Calendar,
    parameters: [
      { id: "baselineVariation", label: "Baseline Variation (%)", type: "number", min: 5, max: 25, default: 10 },
      { id: "peakMultiplier", label: "Peak Multiplier", type: "number", min: 1.5, max: 5, default: 2.5 },
      { id: "peakMonths", label: "Peak Months", type: "text", placeholder: "e.g., 3,6,9,12", default: "11,12" }
    ]
  },
  {
    id: "stepChange",
    name: "Step Change",
    description: "Sudden increase from new service adoption or migration",
    icon: TrendingUp,
    parameters: [
      { id: "stepMonth", label: "Change Month", type: "number", min: 2, max: 11, default: 4 },
      { id: "stepMultiplier", label: "Cost Multiplier", type: "number", min: 1.2, max: 5, default: 2 }
    ]
  },
  {
    id: "anomaly",
    name: "Anomaly Detection",
    description: "Include intentional anomalies for testing alerting systems",
    icon: AlertCircle,
    parameters: [
      { id: "anomalyMonth", label: "Anomaly Month", type: "number", min: 2, max: 11, default: 6 },
      { id: "anomalyMultiplier", label: "Anomaly Spike", type: "number", min: 3, max: 20, default: 10 },
      { id: "anomalyDuration", label: "Duration (days)", type: "number", min: 1, max: 7, default: 3 }
    ]
  }
];

const TrendSimulator = () => {
  const [selectedProviders, setSelectedProviders] = useState([]);
  const [monthCount, setMonthCount] = useState(6);
  const [selectedScenario, setSelectedScenario] = useState("linear");
  const [parameters, setParameters] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);

  const currentScenario = scenarios.find(s => s.id === selectedScenario);

  const handleParameterChange = (parameterId, value) => {
    setParameters(prev => ({
      ...prev,
      [parameterId]: value
    }));
  };

  const handleGenerate = async () => {
    if (selectedProviders.length === 0) {
      toast.error("Please select at least one cloud provider");
      return;
    }

    setIsGenerating(true);
    
    try {
      // TODO: Implement API call to generate trend data
      toast.success(`Generating ${monthCount} months of ${currentScenario.name} data...`);
      
      // Simulate API delay
      setTimeout(() => {
        setIsGenerating(false);
        toast.success("Trend data generated successfully!");
      }, 2000);
    } catch (error) {
      toast.error("Failed to generate trend data");
      setIsGenerating(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="max-w-4xl mx-auto"
    >
      <CloudProviderSelector
        selectedProviders={selectedProviders}
        onProviderToggle={setSelectedProviders}
      />

      {/* Timeline Selector */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
            Timeline Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Number of Months: {monthCount}
              </label>
              <input
                type="range"
                min="2"
                max="12"
                value={monthCount}
                onChange={(e) => setMonthCount(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider mt-2"
                style={{
                  background: `linear-gradient(to right, #667eea 0%, #667eea ${((monthCount - 2) / 10) * 100}%, #e5e7eb ${((monthCount - 2) / 10) * 100}%, #e5e7eb 100%)`
                }}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>2</span>
                <span>6</span>
                <span>9</span>
                <span>12</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scenario Selection */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
            Select Scenario
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {scenarios.map((scenario) => {
              const Icon = scenario.icon;
              const isSelected = selectedScenario === scenario.id;
              
              return (
                <motion.div
                  key={scenario.id}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  transition={{ duration: 0.1 }}
                >
                  <Tooltip content={scenario.description}>
                    <div
                      onClick={() => setSelectedScenario(scenario.id)}
                      className={`cursor-pointer rounded-xl p-4 transition-all duration-300 border-2 ${
                        isSelected
                          ? 'border-primary bg-primary/10 dark:bg-primary/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${
                          isSelected
                            ? 'bg-primary text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                        }`}>
                          <Icon size={20} />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-800 dark:text-gray-100">
                            {scenario.name}
                          </h4>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {scenario.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Tooltip>
                </motion.div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Scenario Parameters */}
      {currentScenario && (
        <Card className="mb-8">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
              Scenario Parameters
            </h3>
            <div className="space-y-4">
              {currentScenario.parameters.map((param) => (
                <div key={param.id}>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {param.label}
                  </label>
                  <input
                    type={param.type}
                    min={param.min}
                    max={param.max}
                    placeholder={param.placeholder}
                    defaultValue={param.default}
                    onChange={(e) => handleParameterChange(param.id, e.target.value)}
                    className="mt-1 w-full px-3 py-2 rounded-xl input-glass"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generate Button */}
      <div className="flex justify-center">
        <Button
          onClick={handleGenerate}
          disabled={selectedProviders.length === 0 || isGenerating}
          className="glass px-8 py-3"
        >
          {isGenerating ? (
            <>
              <span className="animate-spin mr-2">⚡</span>
              Generating Trend Data...
            </>
          ) : (
            <>
              <TrendingUp className="mr-2 h-5 w-5" />
              Generate Trend Data
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );
};

export default TrendSimulator;
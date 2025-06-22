import React, { useMemo } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";

const COLORS = [
  "#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8",
  "#82CA9D", "#FFC658", "#FF6B6B", "#4ECDC4", "#45B7D1"
];

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const CURVisualization = ({ data }) => {
  // Process data for visualizations
  const { serviceData, providerData, dailyData, topResources } = useMemo(() => {
    if (!data || data.length === 0) return {
      serviceData: [],
      providerData: [],
      dailyData: [],
      topResources: []
    };

    // Aggregate by service
    const serviceMap = {};
    const providerMap = {};
    const dailyMap = {};
    const resourceMap = {};

    data.forEach(row => {
      // Service aggregation
      const service = row.ServiceName || "Unknown";
      serviceMap[service] = (serviceMap[service] || 0) + parseFloat(row.BilledCost || 0);

      // Provider aggregation
      const provider = row.ProviderName || "Unknown";
      providerMap[provider] = (providerMap[provider] || 0) + parseFloat(row.BilledCost || 0);

      // Daily aggregation
      const date = row.ChargePeriodStart ? new Date(row.ChargePeriodStart).toLocaleDateString() : "Unknown";
      dailyMap[date] = (dailyMap[date] || 0) + parseFloat(row.BilledCost || 0);

      // Resource aggregation
      const resource = row.ResourceName || "Unknown";
      if (resource !== "Unknown") {
        resourceMap[resource] = (resourceMap[resource] || 0) + parseFloat(row.BilledCost || 0);
      }
    });

    // Convert to arrays and sort
    const serviceData = Object.entries(serviceMap)
      .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);

    const providerData = Object.entries(providerMap)
      .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }));

    const dailyData = Object.entries(dailyMap)
      .map(([date, value]) => ({ date, value: Math.round(value * 100) / 100 }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    const topResources = Object.entries(resourceMap)
      .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);

    return { serviceData, providerData, dailyData, topResources };
  }, [data]);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-2 rounded shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
            {payload[0].name || payload[0].payload.name}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {formatCurrency(payload[0].value)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      variants={fadeInUp}
      initial="initial"
      animate="animate"
      className="space-y-6"
    >
      {/* Cost by Service */}
      <Card className="overflow-hidden">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
            Cost by Service (Top 10)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={serviceData}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                height={100}
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <YAxis 
                tickFormatter={formatCurrency}
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="#3B82F6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost by Provider */}
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              Cost by Cloud Provider
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={providerData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {providerData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Resources by Cost */}
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              Top Resources by Cost
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topResources.map((resource, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate max-w-[200px]">
                      {resource.name}
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                    {formatCurrency(resource.value)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Daily Cost Trend */}
      <Card className="overflow-hidden">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-100">
            Daily Cost Trend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <YAxis 
                tickFormatter={formatCurrency}
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#10B981" 
                strokeWidth={2}
                dot={{ fill: '#10B981', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default CURVisualization;
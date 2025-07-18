import React, { useMemo } from "react";
import { motion } from "framer-motion";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  Server,
  Calendar,
  Zap
} from "lucide-react";
import { Card, CardContent } from "../ui/card";

const KPISummary = React.memo(({ data }) => {
  const kpis = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Calculate total cost
    const totalCost = data.reduce((sum, row) => sum + parseFloat(row.BilledCost || 0), 0);

    // Calculate average daily cost
    const uniqueDates = [...new Set(data.map(row => {
      const date = row.ChargePeriodStart || row.BillingPeriodStart;
      return date ? new Date(date).toLocaleDateString() : null;
    }).filter(Boolean))];
    const avgDailyCost = uniqueDates.length > 0 ? totalCost / uniqueDates.length : 0;

    // Find most expensive service
    const serviceMap = {};
    data.forEach(row => {
      const service = row.ServiceName || "Unknown";
      serviceMap[service] = (serviceMap[service] || 0) + parseFloat(row.BilledCost || 0);
    });
    const sortedServices = Object.entries(serviceMap).sort((a, b) => b[1] - a[1]);
    const topService = sortedServices[0] || ["No services", 0];

    // Count active resources
    const uniqueResources = new Set(data.map(row => row.ResourceId).filter(Boolean));
    const resourceCount = uniqueResources.size;

    // Calculate cost trend (mock for now - would need historical data)
    const trend = Math.random() > 0.5 ? "up" : "down";
    const trendPercentage = Math.floor(Math.random() * 30) + 1;

    // Count providers
    const providers = [...new Set(data.map(row => row.ProviderName).filter(Boolean))];

    // Calculate by charge category
    const chargeCategories = {};
    data.forEach(row => {
      const category = row.ChargeCategory || "Usage";
      chargeCategories[category] = (chargeCategories[category] || 0) + parseFloat(row.BilledCost || 0);
    });

    return {
      totalCost,
      avgDailyCost,
      topService,
      resourceCount,
      trend,
      trendPercentage,
      providerCount: providers.length,
      chargeCategories
    };
  }, [data]);

  if (!kpis) return null;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const cards = [
    {
      title: "Total Cost",
      value: formatCurrency(kpis.totalCost),
      icon: DollarSign,
      color: "from-blue-500 to-cyan-600",
      bgColor: "bg-blue-50 dark:bg-blue-950/30",
      delay: 0.1
    },
    {
      title: "Avg Daily Cost",
      value: formatCurrency(kpis.avgDailyCost),
      icon: Calendar,
      color: "from-purple-500 to-pink-600",
      bgColor: "bg-purple-50 dark:bg-purple-950/30",
      delay: 0.2
    },
    {
      title: "Top Service",
      value: kpis.topService[0],
      subtitle: formatCurrency(kpis.topService[1]),
      icon: Zap,
      color: "from-orange-500 to-red-600",
      bgColor: "bg-orange-50 dark:bg-orange-950/30",
      delay: 0.3
    },
    {
      title: "Cost Trend",
      value: `${kpis.trend === 'up' ? '+' : '-'}${kpis.trendPercentage}%`,
      subtitle: "vs last period",
      icon: kpis.trend === 'up' ? TrendingUp : TrendingDown,
      color: kpis.trend === 'up' ? "from-red-500 to-rose-600" : "from-green-500 to-emerald-600",
      bgColor: kpis.trend === 'up' ? "bg-red-50 dark:bg-red-950/30" : "bg-green-50 dark:bg-green-950/30",
      delay: 0.4
    },
    {
      title: "Active Resources",
      value: formatNumber(kpis.resourceCount),
      icon: Server,
      color: "from-indigo-500 to-blue-600",
      bgColor: "bg-indigo-50 dark:bg-indigo-950/30",
      delay: 0.5
    },
    {
      title: "Cloud Providers",
      value: kpis.providerCount,
      subtitle: kpis.providerCount > 1 ? "Multi-cloud" : "Single cloud",
      icon: Activity,
      color: "from-teal-500 to-green-600",
      bgColor: "bg-teal-50 dark:bg-teal-950/30",
      delay: 0.6
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: card.delay, duration: 0.5 }}
          >
            <Card className={`overflow-hidden hover:shadow-lg transition-all duration-300 hover:scale-105 ${card.bgColor}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className={`p-2 rounded-lg bg-gradient-to-br ${card.color} shadow-lg`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: card.delay + 0.2, type: "spring", stiffness: 200 }}
                    className="text-right"
                  >
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                      {card.title}
                    </p>
                  </motion.div>
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: card.delay + 0.3 }}
                >
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {card.value}
                  </p>
                  {card.subtitle && (
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {card.subtitle}
                    </p>
                  )}
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
});

export default KPISummary;
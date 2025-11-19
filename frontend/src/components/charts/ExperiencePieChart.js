import React from 'react';
import { Paper, Title, Box } from '@mantine/core';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';
import { renderPercentLabel } from './ChartUtils';

export default function ExperiencePieChart({ data }) {
  if (!data || data.length === 0) return null;

  const isMobile = window.innerWidth < 768;

  return (
    <Paper shadow="sm" p="md" withBorder radius="md" style={{ minWidth: 0 }}>
      <Title order={4} mb="md">🍰 התפלגות ניסיון נדרש</Title>

      <Box style={{ width: '100%', height: isMobile ? 340 : 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart
            margin={{
              top: 10,
              right: 10,
              left: 10,
              bottom: isMobile ? 50 : 10,
            }}
          >
            <Tooltip
              formatter={(v, n, e) => [`${v} משרות`, e?.payload?.name]}
              contentStyle={{
                direction: 'rtl',
                textAlign: 'right',
                borderRadius: '8px',
              }}
            />

            <Legend
              verticalAlign="bottom"
              height={50}
              iconSize={12}
              wrapperStyle={{ fontSize: '12px' }}
            />

            <Pie
              data={data}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={isMobile ? '80%' : '65%'}
              labelLine={false}
              label={renderPercentLabel}
            >
              {data.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.color}
                  stroke="white"
                  strokeWidth={1}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}

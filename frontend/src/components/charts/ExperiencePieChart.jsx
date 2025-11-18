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

  return (
    <Paper shadow="sm" p="lg" withBorder radius="md" style={{ minWidth: 0 }}>
      <Title order={4} mb="md">🍰 התפלגות ניסיון נדרש</Title>
      <Box style={{ width: '100%', height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip formatter={(v, n, e) => [`${v} משרות`, e?.name || n]} />
            <Legend verticalAlign="bottom" height={36} iconSize={14} />
            <Pie
              data={data}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={130}
              labelLine={false}
              label={renderPercentLabel}
            >
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.color} stroke="black" strokeWidth={0.8} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}

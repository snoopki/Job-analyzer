import React from 'react';
import { Paper, Title, Box } from '@mantine/core';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

export default function BarSkillsChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <Paper shadow="sm" p="lg" withBorder radius="md" mb="xl" style={{ minWidth: 0 }}>
      <Title order={4} mb="md">📊 כישורים מבוקשים לפי אחוזים</Title>
      <Box style={{ width: '100%', height: 360, minWidth: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              angle={-20}
              textAnchor="end"
              interval={0}
              height={60}
              tick={{ dy: 30, dx: -15, fontSize: 13 }}
            />
            <YAxis
              domain={[0, 100]}
              tickFormatter={(value) => `${value.toFixed(0)}%`}
              tick={{ dx: -35 }}
            />
            <Tooltip formatter={(v) => `${v}% מהמשרות`} />
            <Legend />
            <Bar dataKey="percent" fill="#2563EB" name="אחוז מהמשרות" />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}

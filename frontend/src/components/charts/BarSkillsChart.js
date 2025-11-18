import React from 'react';
import { Paper, Title, Box } from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';
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
  const isMobile = useMediaQuery('(max-width: 768px)');

  if (!data || data.length === 0) return null;

  return (
    <Paper shadow="sm" p="md" withBorder radius="md" mb="xl" style={{ minWidth: 0 }}>
      <Title order={4} mb="md">📊 כישורים מבוקשים לפי אחוזים</Title>
      
      <Box style={{ width: '100%', height: isMobile ? 500 : 400, minWidth: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={data} 
            layout={isMobile ? "vertical" : "horizontal"}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={!isMobile} horizontal={isMobile} />
            
            <XAxis
              type={isMobile ? "number" : "category"}
              dataKey={isMobile ? undefined : "name"}
              domain={[0, 100]}
              tickFormatter={!isMobile ? undefined : (value) => `${value}%`}
              tick={{ fontSize: 11, fill: '#666', dy: isMobile ? 0 : 8 }}
              angle={!isMobile ? 0 : 0}
              textAnchor={!isMobile ? "middle" : "middle"}
              height={!isMobile ? 60 : 30}
              interval={0}
            />

            <YAxis
              type={isMobile ? "category" : "number"}
              dataKey={isMobile ? "name" : undefined}
              domain={[0, 100]}
              width={isMobile ? 120 : 40} 
              tickFormatter={isMobile ? (val) => val.length > 15 ? val.slice(0, 15) + '..' : val : (val) => `${val}%`}
              tick={{ fontSize: 11, fill: '#666', dx: isMobile ? -50 : -25 }} 
              interval={0}
            />

            <Tooltip 
              cursor={{ fill: 'transparent' }}
              formatter={(v) => `${v}% מהמשרות`}
              contentStyle={{ direction: 'rtl', textAlign: 'right', borderRadius: '8px' }}
            />
            
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            
            <Bar 
              dataKey="percent" 
              fill="#2563EB" 
              name="אחוז מהמשרות" 
              radius={isMobile ? [0, 4, 4, 0] : [4, 4, 0, 0]} 
              barSize={isMobile ? 20 : 40}
            />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}
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
      
      <Box style={{ width: '100%', height: isMobile ? Math.max(500, data.length * 60) : 420, minWidth: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={data} 
            layout={isMobile ? "vertical" : "horizontal"}
            margin={{ 
              top: 20, 
              right: isMobile ? 10 : 30, 
              left: isMobile ? 5 : 20, 
              bottom: isMobile ? 10 : 60 
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={!isMobile} horizontal={isMobile} />
            
            <XAxis
              type={isMobile ? "number" : "category"}
              dataKey={isMobile ? undefined : "name"}
              domain={[0, 100]}
              ticks={isMobile ? [0, 25, 50, 75, 100] : undefined}
              tickFormatter={!isMobile ? undefined : (value) => `${value}%`}
              tick={{ fontSize: isMobile ? 10 : 11, fill: '#b2bbb4ff' }}
              interval={isMobile ? 0 : "preserveStartEnd"}
              angle={isMobile ? 0 : -45}
              textAnchor={isMobile ? "middle" : "middle"}
              height={isMobile ? 30 : 60}
              orientation="top"
              axisLine={false}
              tickLine={false}

            />

            <YAxis
              type={isMobile ? "category" : "number"}
              dataKey={isMobile ? "name" : undefined}
              domain={[0, 100]}
              width={isMobile ? 100 : 50} 
              tickFormatter={isMobile ? (val) => val.length > 12 ? val.slice(0, 12) + '..' : val : (val) => `${val}%`}
              tick={{ fontSize: isMobile ? 10 : 11, fill: '#b2bbb4ff' }} 
              interval={0}
              orientation="right"

              axisLine={false}
              tickLine={false}
            />

            <Tooltip 
              cursor={{ fill: 'transparent' }}
              formatter={(v) => `${v}% מהמשרות`}
              contentStyle={{ 
                direction: 'rtl', 
                textAlign: 'right', 
                borderRadius: '8px',
                fontSize: isMobile ? 11 : 13,
                padding: isMobile ? 8 : 10,
                maxWidth: isMobile ? 150 : 220,
                whiteSpace: "normal",
              }}
            />
            
            <Legend 
              wrapperStyle={{ 
                paddingTop: isMobile ? '5px' : '10px',
                fontSize: isMobile ? '11px' : '13px'
              }} 
            />
            
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


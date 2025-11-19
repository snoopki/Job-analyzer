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
      
      <Box
        style={{
          width: '100%',
          height: isMobile ? Math.max(500, data.length * 60) : 420,
          minWidth: 0
        }}
      >
        <ResponsiveContainer
          width="100%"
          height="100%"
          minWidth={0}  // חשוב במובייל כדי לא לדחוס
        >
          <BarChart
            data={data}
            layout={isMobile ? "vertical" : "horizontal"}
            margin={{
              top: 20,
              bottom: 20,
              left: isMobile ? 10 : 30,
              right: isMobile ? 10 : 30,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={!isMobile}
              horizontal={isMobile}
            />

            {/* X AXIS — במובייל זה אחוזים ולכן צריך מלא רוחב */}
            <XAxis
              type={isMobile ? "number" : "category"}
              dataKey={isMobile ? undefined : "name"}
              domain={[0, 100]}
              ticks={isMobile ? [0, 25, 50, 75, 100] : undefined}
              tickFormatter={isMobile ? (v) => `${v}%` : undefined}
              tick={{ fontSize: isMobile ? 10 : 11, fill: '#b2bbb4ff' }}

              interval={0}
              angle={0}

              height={isMobile ? 30 : 60}
              axisLine={false}
              tickLine={false}
            />

            {/* Y AXIS — כאן הבעיה הייתה. הקטנו רוחב כדי לאכול פחות מהרוחב הכולל */}
            <YAxis
              type={isMobile ? "category" : "number"}
              dataKey={isMobile ? "name" : undefined}
              domain={[0, 100]}
              width={isMobile ? 60 : 50} 
              tickFormatter={
                isMobile
                  ? (v) => (v.length > 12 ? v.slice(0, 12) + '..' : v)
                  : (v) => `${v}%`
              }
              tick={{ fontSize: isMobile ? 10 : 11, fill: '#b2bbb4ff' }}
              interval={0}
              axisLine={false}
              tickLine={false}
              orientation="right"
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
                whiteSpace: "normal",
              }}
            />

            <Legend
              wrapperStyle={{
                paddingTop: isMobile ? '5px' : '10px',
                fontSize: isMobile ? '11px' : '13px',
              }}
            />

            <Bar
              dataKey="percent"
              fill="#2563EB"
              name="אחוז מהמשרות"
              radius={isMobile ? [0, 4, 4, 0] : [4, 4, 0, 0]}
              barSize={isMobile ? 22 : 40}
            />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}

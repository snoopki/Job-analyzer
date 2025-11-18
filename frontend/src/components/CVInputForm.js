import { useState } from 'react';
import { Title, Textarea, Button, Paper } from '@mantine/core';

function CVInputForm({ isLoading, onSubmit }) {
  const [cvText, setCvText] = useState("");

  const handleSubmit = () => {
    if (cvText.trim()) {
      onSubmit(cvText);
    }
  };

  return (
    <Paper shadow="sm" p={{ base: 'md', sm: 'xl' }} withBorder>
      <Title order={2} ta="center" mb="lg" size="h3">
        מנתח קורות חיים AI
      </Title>
      <Textarea
        label="הדבק את קורות החיים שלך"
        placeholder="כאן המקום להדביק את הטקסט המלא..."
        autosize
        minRows={5}
        maxRows={15}
        size="md"
        value={cvText}
        onChange={(event) => setCvText(event.currentTarget.value)}
      />
      <Button
        fullWidth
        mt="xl"
        size="lg"
        onClick={handleSubmit}
        loading={isLoading}
        disabled={!cvText.trim()}
      >
        {isLoading ? 'מנתח...' : 'נתח את קורות החיים שלי'}
      </Button>
    </Paper>
  );
}

export default CVInputForm;
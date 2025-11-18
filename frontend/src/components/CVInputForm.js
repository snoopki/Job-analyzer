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
    <Paper shadow="sm" p="xl" withBorder>
      <Title order={2} ta="center" mb="lg">
        מנתח קורות חיים AI
      </Title>
      <Textarea
        label="הדבק את קורות החיים שלך"
        placeholder="כאן המקום להדביק את הטקסט המלא של קורות החיים שלך..."
        autosize
        minRows={10}
        maxRows={20}
        size="md"
        value={cvText}
        onChange={(event) => setCvText(event.currentTarget.value)}
      />
      <Button
        fullWidth
        mt="xl"
        size="lg"
        onClick={handleSubmit}
        disabled={isLoading || !cvText.trim()}
      >
        {isLoading ? 'מנתח...' : 'נתח את קורות החיים שלי'}
      </Button>
    </Paper>
  );
}

export default CVInputForm;
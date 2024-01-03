# Exemple de récupération des thèmes
user_input_themes = self.theme_input.toPlainText().strip()
user_entered_themes = [theme.strip() for theme in user_input_themes.split(",")]

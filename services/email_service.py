import resend

from core.config import settings


def _build_reset_email_html(reset_url: str) -> str:
    expire_minutes = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Réinitialisation de mot de passe — BankPulse</title>
</head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 1px 3px rgba(0,0,0,0.1);">
          <!-- Header -->
          <tr>
            <td style="background:#4f46e5;padding:24px 32px;">
              <p style="margin:0;color:#ffffff;font-size:20px;font-weight:700;">
                BankPulse
              </p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:32px;">
              <h1 style="margin:0 0 16px;font-size:22px;color:#111827;">
                Réinitialisation de votre mot de passe
              </h1>
              <p style="margin:0 0 24px;color:#374151;line-height:1.6;">
                Vous avez demandé à réinitialiser votre mot de passe BankPulse.
                Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe.
              </p>
              <p style="margin:0 0 24px;">
                <a href="{reset_url}"
                   style="display:inline-block;background:#4f46e5;color:#ffffff;
                          padding:12px 24px;border-radius:6px;text-decoration:none;
                          font-weight:600;font-size:15px;">
                  Réinitialiser mon mot de passe
                </a>
              </p>
              <p style="margin:0 0 16px;color:#6b7280;font-size:13px;line-height:1.5;">
                Ce lien expire dans <strong>{expire_minutes} minutes</strong>.
                Si vous n'avez pas demandé à réinitialiser votre mot de passe,
                vous pouvez ignorer cet email en toute sécurité.
              </p>
              <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;" />
              <p style="margin:0;color:#9ca3af;font-size:12px;">
                Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br />
                <a href="{reset_url}" style="color:#4f46e5;word-break:break-all;">
                  {reset_url}
                </a>
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:16px 32px;background:#f9fafb;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;">
                © BankPulse — Analyse financière personnelle
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _build_share_invitation_html(
    inviter_name: str, account_name: str, invitation_url: str
) -> str:
    expire_days = settings.SHARE_INVITATION_EXPIRE_DAYS
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Invitation BankPulse</title>
</head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 1px 3px rgba(0,0,0,0.1);">
          <!-- Header -->
          <tr>
            <td style="background:#4f46e5;padding:24px 32px;">
              <p style="margin:0;color:#ffffff;font-size:20px;font-weight:700;">
                BankPulse
              </p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:32px;">
              <h1 style="margin:0 0 16px;font-size:22px;color:#111827;">
                {inviter_name} vous invite à accéder à un compte
              </h1>
              <p style="margin:0 0 24px;color:#374151;line-height:1.6;">
                <strong>{inviter_name}</strong> souhaite partager avec vous l'accès au compte
                <strong>{account_name}</strong> sur BankPulse.
              </p>
              <p style="margin:0 0 24px;">
                <a href="{invitation_url}"
                   style="display:inline-block;background:#4f46e5;color:#ffffff;
                          padding:12px 24px;border-radius:6px;text-decoration:none;
                          font-weight:600;font-size:15px;">
                  Voir l'invitation
                </a>
              </p>
              <p style="margin:0 0 16px;color:#6b7280;font-size:13px;line-height:1.5;">
                Ce lien expire dans <strong>{expire_days} jours</strong>.
                Si vous ne connaissez pas {inviter_name}, ignorez cet email.
              </p>
              <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;" />
              <p style="margin:0;color:#9ca3af;font-size:12px;">
                Lien direct :
                <a href="{invitation_url}" style="color:#4f46e5;word-break:break-all;">
                  {invitation_url}
                </a>
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:16px 32px;background:#f9fafb;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;">
                © BankPulse — Analyse financière personnelle
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


class EmailService:
    def send_password_reset(self, to_email: str, reset_url: str) -> None:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(
            {
                "from": "BankPulse <contact@contact.chleo-consulting.fr>",
                "to": [to_email],
                "subject": "Réinitialisation de votre mot de passe BankPulse",
                "html": _build_reset_email_html(reset_url),
            }
        )

    def send_account_share_invitation(
        self,
        to_email: str,
        inviter_name: str,
        account_name: str,
        invitation_url: str,
    ) -> None:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(
            {
                "from": "BankPulse <contact@contact.chleo-consulting.fr>",
                "to": [to_email],
                "subject": f"{inviter_name} vous invite à accéder à un compte sur BankPulse",
                "html": _build_share_invitation_html(inviter_name, account_name, invitation_url),
            }
        )

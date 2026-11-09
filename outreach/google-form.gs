/**
 * zhol · Google Form for traffic offices: six one-tap questions and an optional contact.
 *
 * How to use (one minute, from a laptop):
 *   1. Open https://script.new while signed in to the Google account that should own the form.
 *   2. Delete what is there, paste this whole file, press Save.
 *   3. Choose createZholForm at the top and press Run. Allow access when Google asks
 *      (it needs Forms, Sheets and fetching the mascot picture from our site).
 *   4. Open "Execution log": it shows the link to send, the edit link and the answers sheet.
 *
 * The answer labels must stay the same as in scripts/survey_summary.py (GOOGLE_FORM), which reads the
 * CSV of this form; tests/test_survey.py checks that they match.
 */
function createZholForm() {
  var form = FormApp.create('zhol · Sette domande per gli uffici traffico');
  form.setTitle('Sette domande. Un minuto.')
    .setDescription('Quanto vi costano divieti, code, chiusure e scioperi, su strada, rotaia o traghetto? Ricerca del team zhol ' +
      'dell’Università Bocconi per TEF Ignition 2026. Si risponde con un tocco, è anonimo e non vendiamo nulla. ' +
      'Pubblichiamo solo dati aggregati.')
    .setCollectEmail(false)
    .setAllowResponseEdits(false)
    .setShowLinkToRespondAgain(false)
    .setProgressBar(false)
    .setConfirmationMessage('Grazie! Ci avete aiutato molto. Conoscete un altro ufficio traffico? ' +
      'Inoltrategli questo modulo: ogni risposta in più rende i numeri più solidi.');
  // Accounts of a school or company (e.g. Bocconi) restrict forms to their own domain by default:
  // hauliers would have to sign in. Open it to everyone; on a personal Gmail this call is not needed.
  try { form.setRequireLogin(false); } catch (e) { /* personal account: already open */ }

  // Zholdas, the mascot, next to his truck (served by the site)
  try {
    var picture = UrlFetchApp.fetch('https://zhol.live/assets/img/mascot/truck-form.jpg').getBlob();
    form.addImageItem().setImage(picture).setAlignment(FormApp.Alignment.CENTER).setWidth(300);
  } catch (e) {
    Logger.log('Picture not added (the form works without it): ' + e);
  }

  var questions = [
    ['Quanti mezzi gestite (camion, rimorchi, container, vagoni)?',
      ['1–5', '6–20', '21–50', '51–100', 'Più di 100']],
    ['Quante spedizioni a settimana vanno all’estero, su strada, rotaia o traghetto?',
      ['Mai', '1–5 volte', '6–20 volte', 'Più di 20 volte']],
    ['Quanto tempo passate ogni giorno a controllare divieti, code e scioperi?',
      ['Meno di 10 minuti', '10–20 minuti', '20–40 minuti', 'Più di 40 minuti']],
    ['Nell’ultimo mese, quante volte un divieto, una coda, una chiusura o uno sciopero vi ha costretto a cambiare una spedizione (orario, percorso o data)?',
      ['Mai', '1–2 volte', '3–5 volte', '6–10 volte', 'Più di 10 volte']],
    ['L’ultima volta che un divieto, una coda o uno sciopero ha fermato una vostra spedizione, quanto vi è costato?',
      ['Meno di 100 €', '100–300 €', '300–1.000 €', '1.000–3.000 €', 'Più di 3.000 €', 'Non lo so']],
    ['Se altri uffici vi avvisassero di una coda o di una chiusura vista dai loro autisti, prima che partano i vostri camion, condividereste anche le vostre?',
      ['Sì, volentieri', 'Sì, se resta anonimo', 'Vorrei solo riceverle', 'No']],
    ['Quale prezzo vi sembra giusto, al mese per ogni mezzo?',
      ['Niente, non pagherei', 'Fino a 5 €', '5–10 €', '10–20 €', 'Più di 20 €']]
  ];
  questions.forEach(function (q) {
    form.addMultipleChoiceItem().setTitle(q[0]).setChoiceValues(q[1]).setRequired(true);
  });

  // optional, on the same page so the seven answers are never lost if someone stops here
  form.addSectionHeaderItem()
    .setTitle('Facoltativo: volete qualcosa in cambio?')
    .setHelpText('Se lasciate un contatto lo usiamo solo per ciò che avete scelto e lo cancelliamo a fine progetto, ' +
      'o prima se ce lo chiedete.');
  form.addCheckboxItem().setTitle('Cosa vi interessa?')
    .setChoiceValues(['I risultati del sondaggio',
      'Un posto tra i primi uffici della rete condivisa']);
  form.addTextItem().setTitle('Email o telefono aziendale');
  form.addCheckboxItem().setTitle('Consenso')
    .setChoiceValues(['Potete usare questo contatto solo per ciò che ho scelto.']);

  // every answer also lands in a Google Sheet
  var sheet = SpreadsheetApp.create('zhol · risposte al sondaggio');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  var link = form.getPublishedUrl();
  try { link = form.shortenFormUrl(link); } catch (e) { /* the long link works too */ }
  Logger.log('LINK TO SEND: ' + link);
  Logger.log('Edit the form: ' + form.getEditUrl());
  Logger.log('Answers sheet: ' + sheet.getUrl());
}

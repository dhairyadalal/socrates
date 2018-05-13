@Stateful
@Name("sampleSetAction")
@Scope(ScopeType.SESSION)
public class SampleSetActionBean implements SampleSetAction {

  private String sampleSetName;
  private InputStream data;

  @EJB
  private SampleManager sampleManager;
  ...
  public void importSampleSet() { ... }
  ...
}
